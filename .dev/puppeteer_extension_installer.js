#!/usr/bin/env node
/**
 * Puppeteer-based Chrome Extension Installer for SciTeX Scholar
 * 
 * This script uses Puppeteer to automate Chrome extension installation
 * with better handling of Chrome's security features.
 */

const puppeteer = require('puppeteer');
const fs = require('fs').promises;
const path = require('path');
const https = require('https');
const { promisify } = require('util');
const stream = require('stream');
const pipeline = promisify(stream.pipeline);

class PuppeteerExtensionInstaller {
    constructor() {
        this.extensions = {
            lean_library: {
                id: 'hghakoefmnkhamdhenpbogkeopjlkpoa',
                name: 'Lean Library'
            },
            zotero_connector: {
                id: 'ekhagklcjbdpajgpjgmbionohlpdbjgc',
                name: 'Zotero Connector'
            },
            accept_cookies: {
                id: 'ofpnikijgfhlmmjlpkfaifhhdonchhoi',
                name: 'Accept all cookies'
            },
            captcha_solver: {
                id: 'ifibfemgeogfhoebkmokieepdoobkbpo',
                name: 'Captcha Solver'
            }
        };
        
        this.profileDir = path.join(process.env.HOME, '.scitex', 'scholar', 'chrome_profile');
        this.extensionsDir = path.join(process.env.HOME, '.scitex', 'scholar', 'extensions');
    }
    
    async ensureDirectories() {
        await fs.mkdir(this.profileDir, { recursive: true });
        await fs.mkdir(this.extensionsDir, { recursive: true });
    }
    
    async downloadCRX(extensionId, outputPath) {
        const url = `https://clients2.google.com/service/update2/crx?response=redirect&prodversion=120.0&acceptformat=crx3&x=id%3D${extensionId}%26installsource%3Dondemand%26uc`;
        
        return new Promise((resolve, reject) => {
            https.get(url, { 
                headers: {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            }, (response) => {
                if (response.statusCode === 302 || response.statusCode === 301) {
                    // Follow redirect
                    https.get(response.headers.location, async (redirectResponse) => {
                        const writeStream = require('fs').createWriteStream(outputPath);
                        await pipeline(redirectResponse, writeStream);
                        resolve(outputPath);
                    });
                } else {
                    const writeStream = require('fs').createWriteStream(outputPath);
                    pipeline(response, writeStream)
                        .then(() => resolve(outputPath))
                        .catch(reject);
                }
            }).on('error', reject);
        });
    }
    
    async installWithPuppeteer() {
        await this.ensureDirectories();
        
        // Download CRX files first
        const crxPaths = [];
        for (const [key, ext] of Object.entries(this.extensions)) {
            const crxPath = path.join(this.extensionsDir, `${key}.crx`);
            
            try {
                await fs.access(crxPath);
                console.log(`✓ ${ext.name} CRX already downloaded`);
            } catch {
                console.log(`Downloading ${ext.name}...`);
                await this.downloadCRX(ext.id, crxPath);
                console.log(`✓ Downloaded ${ext.name}`);
            }
            
            crxPaths.push(crxPath);
        }
        
        // Launch browser with extensions
        console.log('\nLaunching Chrome with extensions...');
        
        const browser = await puppeteer.launch({
            headless: false,
            executablePath: '/usr/bin/google-chrome-stable', // Adjust for your system
            userDataDir: this.profileDir,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                `--disable-extensions-except=${crxPaths.join(',')}`,
                `--load-extension=${crxPaths.join(',')}`
            ]
        });
        
        const page = await browser.newPage();
        
        // Navigate to extensions page to verify
        await page.goto('chrome://extensions/', { waitUntil: 'networkidle0' });
        
        console.log('\nExtensions page loaded. Verify extensions are installed.');
        console.log('Browser will remain open for manual verification.');
        
        // Keep browser open
        await new Promise(resolve => {
            process.stdin.resume();
            console.log('\nPress Ctrl+C to exit...');
            process.on('SIGINT', () => {
                browser.close();
                resolve();
            });
        });
    }
    
    async installViaWebStore() {
        console.log('\n=== Installing via Chrome Web Store ===');
        
        const browser = await puppeteer.launch({
            headless: false,
            userDataDir: this.profileDir,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        
        const page = await browser.newPage();
        
        for (const [key, ext] of Object.entries(this.extensions)) {
            console.log(`\nInstalling ${ext.name}...`);
            
            try {
                await page.goto(`https://chrome.google.com/webstore/detail/${ext.id}`, {
                    waitUntil: 'networkidle0'
                });
                
                // Wait for "Add to Chrome" button
                await page.waitForSelector('button[jsaction*="install"]', { timeout: 10000 });
                
                // Click install button
                await page.click('button[jsaction*="install"]');
                
                // Wait for confirmation dialog
                await page.waitForTimeout(2000);
                
                // Try to click confirmation
                const frames = page.frames();
                for (const frame of frames) {
                    try {
                        await frame.click('button[jsaction*="confirm"]');
                        console.log(`✓ ${ext.name} installation initiated`);
                        break;
                    } catch {}
                }
                
                await page.waitForTimeout(3000);
                
            } catch (error) {
                console.log(`✗ Failed to install ${ext.name}: ${error.message}`);
            }
        }
        
        console.log('\nKeeping browser open for verification...');
        await page.goto('chrome://extensions/');
        
        await new Promise(resolve => {
            console.log('Press Ctrl+C to exit...');
            process.on('SIGINT', () => {
                browser.close();
                resolve();
            });
        });
    }
}

// Main execution
async function main() {
    const installer = new PuppeteerExtensionInstaller();
    
    console.log('Puppeteer Chrome Extension Installer');
    console.log('====================================\n');
    
    const args = process.argv.slice(2);
    
    if (args.includes('--webstore')) {
        await installer.installViaWebStore();
    } else {
        await installer.installWithPuppeteer();
    }
}

// Run the installer
main().catch(console.error);