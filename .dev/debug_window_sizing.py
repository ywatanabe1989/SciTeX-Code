#!/usr/bin/env python3
"""
Debug Window Sizing Issue

Investigate why --window-size and --window-position arguments aren't working
"""

import asyncio
from playwright.async_api import async_playwright

async def debug_window_sizing():
    print('🔍 Debugging Window Sizing Arguments')
    print('='*50)
    
    playwright = await async_playwright().start()
    
    try:
        print('🧪 Test 1: Basic window sizing')
        browser = await playwright.chromium.launch(
            headless=False,
            args=[
                "--window-size=400,300",
                "--window-position=10,10",
                "--no-sandbox"
            ]
        )
        
        context = await browser.new_context()
        page = await context.new_page()
        
        # Get actual window dimensions
        dimensions = await page.evaluate('''
            () => {
                return {
                    windowWidth: window.innerWidth,
                    windowHeight: window.innerHeight,
                    screenWidth: window.screen.width,
                    screenHeight: window.screen.height,
                    windowX: window.screenX,
                    windowY: window.screenY
                };
            }
        ''')
        
        print(f'📐 Requested: 400x300 at (10,10)')
        print(f'📐 Actual: {dimensions["windowWidth"]}x{dimensions["windowHeight"]} at ({dimensions["windowX"]},{dimensions["windowY"]})')
        print(f'🖥️  Screen: {dimensions["screenWidth"]}x{dimensions["screenHeight"]}')
        
        await browser.close()
        
        print('\n🧪 Test 2: Using viewport instead')
        browser = await playwright.chromium.launch(
            headless=False,
            args=["--no-sandbox"]
        )
        
        # Set viewport size instead
        context = await browser.new_context(
            viewport={'width': 400, 'height': 300}
        )
        page = await context.new_page()
        
        # Check viewport vs window
        viewport_info = await page.evaluate('''
            () => {
                return {
                    viewportWidth: document.documentElement.clientWidth,
                    viewportHeight: document.documentElement.clientHeight,
                    windowWidth: window.innerWidth,
                    windowHeight: window.innerHeight
                };
            }
        ''')
        
        print(f'📐 Viewport: {viewport_info["viewportWidth"]}x{viewport_info["viewportHeight"]}')
        print(f'📐 Window: {viewport_info["windowWidth"]}x{viewport_info["windowHeight"]}')
        
        await browser.close()
        
        print('\n🧪 Test 3: Manual window resize')
        browser = await playwright.chromium.launch(
            headless=False,
            args=["--no-sandbox"]
        )
        
        context = await browser.new_context()
        page = await context.new_page()
        
        # Try to resize programmatically
        await page.evaluate('''
            () => {
                window.resizeTo(400, 300);
                window.moveTo(10, 10);
            }
        ''')
        
        await asyncio.sleep(1)
        
        final_dimensions = await page.evaluate('''
            () => {
                return {
                    windowWidth: window.innerWidth,
                    windowHeight: window.innerHeight,
                    windowX: window.screenX,
                    windowY: window.screenY
                };
            }
        ''')
        
        print(f'📐 After resize: {final_dimensions["windowWidth"]}x{final_dimensions["windowHeight"]} at ({final_dimensions["windowX"]},{final_dimensions["windowY"]})')
        
        await browser.close()
        
    except Exception as e:
        print(f'❌ Debug failed: {e}')
    
    finally:
        await playwright.stop()
    
    print('\n💡 Recommendations:')
    print('1. Use context viewport for content sizing')
    print('2. Window arguments may be ignored by some window managers')
    print('3. Programmatic resize might work better')

if __name__ == "__main__":
    asyncio.run(debug_window_sizing())