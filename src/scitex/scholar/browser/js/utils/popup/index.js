/**
 * Popup handling utilities
 * 
 * This module provides functions for detecting and handling various types of
 * popups that commonly appear on academic publisher websites.
 * 
 * Files:
 * - popup_detector.js: Core popup detection and handling functions
 * 
 * Usage:
 * These functions are designed to be injected into web pages via 
 * page.evaluate() in Playwright/Puppeteer automation.
 */

// Re-export popup detector functions
// When using a bundler, this would properly export the module
// For now, individual files should be loaded directly