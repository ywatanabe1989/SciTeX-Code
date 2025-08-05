#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Interactive OpenAthens debug with step-by-step manual verification

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from playwright.async_api import async_playwright


async def interactive_debug():
    """Interactive debug session to understand OpenAthens behavior."""
    print("🔍 Interactive OpenAthens Debug Session")
    print("=" * 50)
    
    async with async_playwright() as p:
        # Launch browser in visible mode
        browser = await p.chromium.launch(
            headless=False,
            args=['--no-sandbox', '--disable-web-security']
        )
        
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720}
        )
        
        page = await context.new_page()
        
        print("🌐 Step 1: Navigate to OpenAthens")
        await page.goto("https://my.openathens.net/?passiveLogin=false")
        input("Press Enter when page loads...")
        
        print("🍪 Step 2: Handle cookies")
        # Try to click cookie acceptance
        try:
            cookie_btn = await page.wait_for_selector('button:has-text("Accept all cookies")', timeout=5000)
            if cookie_btn:
                await cookie_btn.click()
                print("✅ Cookies accepted")
        except:
            print("⚠️  No cookie banner found")
        
        input("Press Enter after cookies are handled...")
        
        print("📧 Step 3: Fill email")
        email_field = await page.wait_for_selector('input[placeholder*="Institution"]')
        await email_field.fill("Yusuke.Watanabe@unimelb.edu.au")
        print("✅ Email filled")
        
        input("Press Enter after email is filled and you see any changes...")
        
        print("🔍 Step 4: Analyze page state")
        page_state = await page.evaluate("""
            () => {
                const elements = Array.from(document.querySelectorAll('*'));
                const unimelb_elements = elements.filter(el => 
                    el.textContent && el.textContent.includes('University of Melbourne')
                );
                
                return {
                    unimelb_count: unimelb_elements.length,
                    unimelb_elements: unimelb_elements.map(el => ({
                        tag: el.tagName,
                        text: el.textContent.substring(0, 100),
                        visible: el.offsetParent !== null,
                        clickable: el.onclick !== null || el.addEventListener !== undefined,
                        classes: el.className,
                        id: el.id
                    })),
                    all_visible_text: document.body.innerText
                };
            }
        """)
        
        print(f"🎯 Found {page_state['unimelb_count']} UniMelb elements:")
        for i, elem in enumerate(page_state['unimelb_elements']):
            print(f"  {i+1}. {elem['tag']} - Visible: {elem['visible']} - Text: {elem['text'][:50]}...")
            print(f"     Classes: {elem['classes']}, ID: {elem['id']}")
        
        if page_state['unimelb_count'] > 0:
            print("\n🖱️  Step 5: Try clicking University of Melbourne")
            
            # Try different click strategies
            click_success = await page.evaluate("""
                () => {
                    const elements = Array.from(document.querySelectorAll('*'));
                    const unimelb_elements = elements.filter(el => 
                        el.textContent && el.textContent.includes('University of Melbourne')
                    );
                    
                    for (let i = 0; i < unimelb_elements.length; i++) {
                        const element = unimelb_elements[i];
                        try {
                            // Try direct click
                            element.click();
                            return 'success_direct_' + i;
                        } catch (e1) {
                            try {
                                // Try parent click
                                element.parentElement.click();
                                return 'success_parent_' + i;
                            } catch (e2) {
                                try {
                                    // Try mouse event
                                    const event = new MouseEvent('click', {bubbles: true});
                                    element.dispatchEvent(event);
                                    return 'success_event_' + i;
                                } catch (e3) {
                                    continue;
                                }
                            }
                        }
                    }
                    return 'all_failed';
                }
            """)
            
            print(f"Click result: {click_success}")
            
            # Wait and check for navigation
            await asyncio.sleep(3)
            current_url = page.url
            print(f"Current URL after click: {current_url}")
            
            if current_url != "https://my.openathens.net/?passiveLogin=false":
                print("✅ Successfully navigated away from OpenAthens!")
                print("🎉 Institution selection worked!")
                
                # Take screenshot of success
                await page.screenshot(path=str(Path(__file__).parent / "openathens_success_manual.png"))
                
                # Analyze the new page
                new_page_info = await page.evaluate("""
                    () => ({
                        title: document.title,
                        url: window.location.href,
                        hasLoginForm: !!document.querySelector('input[type="password"], input[name*="password"], input[name*="identifier"]'),
                        formCount: document.querySelectorAll('form').length,
                        inputCount: document.querySelectorAll('input').length
                    })
                """)
                
                print(f"New page info: {new_page_info}")
                
            else:
                print("❌ Still on OpenAthens page - selection didn't work")
        
        else:
            print("❌ No University of Melbourne elements found!")
        
        input("Press Enter to close browser...")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(interactive_debug())