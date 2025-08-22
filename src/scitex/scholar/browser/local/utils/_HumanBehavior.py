#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 08:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/local/utils/_HumanBehavior.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/local/utils/_HumanBehavior.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio
import random
from typing import Optional, Tuple

from playwright.async_api import Page

from scitex import log

logger = log.getLogger(__name__)


class HumanBehavior:
    """Simulates human-like behavior patterns for browser automation."""
    
    @staticmethod
    async def random_delay_async(
        min_ms: int = 1000, 
        max_ms: int = 3000,
        description: str = None
    ) -> None:
        """Add random delay to simulate human timing."""
        delay_ms = random.randint(min_ms, max_ms)
        if description:
            logger.debug(f"Human delay: {description} ({delay_ms}ms)")
        await asyncio.sleep(delay_ms / 1000)
    
    @staticmethod
    async def reading_delay_async(content_length: int = 1000) -> None:
        """Simulate time taken to read content based on length."""
        # Avg human reading speed: 200-250 words/minute
        # Assume ~5 chars per word
        words = content_length / 5
        reading_time_ms = (words / 250) * 60 * 1000  # Convert to milliseconds
        reading_time_ms = min(max(reading_time_ms, 2000), 10000)  # Clamp between 2-10 seconds
        
        # Add randomness
        actual_delay = reading_time_ms * random.uniform(0.8, 1.2)
        logger.debug(f"Reading delay: {actual_delay:.0f}ms for {content_length} chars")
        await asyncio.sleep(actual_delay / 1000)
    
    @staticmethod
    async def mouse_move_async(
        page: Page, 
        x: Optional[int] = None, 
        y: Optional[int] = None
    ) -> None:
        """Move mouse to position with human-like movement."""
        if x is None:
            x = random.randint(100, 1200)
        if y is None:
            y = random.randint(100, 800)
        
        # Move in steps for more natural movement
        current_x, current_y = 0, 0
        steps = random.randint(3, 7)
        
        for i in range(steps):
            progress = (i + 1) / steps
            # Ease-in-out curve
            t = progress * progress * (3.0 - 2.0 * progress)
            
            next_x = int(current_x + (x - current_x) * t)
            next_y = int(current_y + (y - current_y) * t)
            
            await page.mouse.move(next_x, next_y)
            await asyncio.sleep(random.uniform(0.01, 0.03))
            
            current_x, current_y = next_x, next_y
    
    @staticmethod
    async def hover_and_click_async(
        page: Page,
        selector: str = None,
        element = None
    ) -> None:
        """Hover over element before clicking with human-like timing."""
        if selector:
            element = page.locator(selector)
        
        if not element:
            raise ValueError("Either selector or element must be provided")
        
        # Move to element area first
        box = await element.bounding_box()
        if box:
            # Add small offset to avoid clicking exact center every time
            offset_x = random.randint(-10, 10)
            offset_y = random.randint(-10, 10)
            target_x = box['x'] + box['width'] / 2 + offset_x
            target_y = box['y'] + box['height'] / 2 + offset_y
            
            await HumanBehavior.mouse_move_async(page, int(target_x), int(target_y))
        
        # Hover
        await element.hover()
        await HumanBehavior.random_delay_async(200, 800, "hover before click")
        
        # Click
        await element.click()
        logger.debug("Performed human-like hover and click")
    
    @staticmethod
    async def scroll_async(
        page: Page,
        direction: str = "down",
        distance: Optional[int] = None
    ) -> None:
        """Scroll page with human-like behavior."""
        if distance is None:
            distance = random.randint(300, 800)
        
        if direction == "up":
            distance = -distance
        
        # Scroll in small chunks for more natural behavior
        chunks = random.randint(2, 5)
        for i in range(chunks):
            chunk_distance = distance // chunks
            # Add some variation
            chunk_distance += random.randint(-50, 50)
            
            await page.evaluate(f"window.scrollBy(0, {chunk_distance})")
            await HumanBehavior.random_delay_async(100, 300)
        
        logger.debug(f"Scrolled {direction} ~{abs(distance)}px in {chunks} chunks")
    
    @staticmethod
    async def type_text_async(
        page: Page,
        selector: str = None,
        element = None,
        text: str = "",
        clear_first: bool = False
    ) -> None:
        """Type text with human-like timing and occasional mistakes."""
        if selector:
            element = page.locator(selector)
        
        if not element:
            raise ValueError("Either selector or element must be provided")
        
        # Click to focus
        await element.click()
        await HumanBehavior.random_delay_async(100, 300)
        
        # Clear if requested
        if clear_first:
            await element.clear()
            await HumanBehavior.random_delay_async(100, 200)
        
        # Type character by character
        for i, char in enumerate(text):
            # Occasionally make a typo and correct it (1% chance)
            if random.random() < 0.01 and i > 0:
                wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                await element.type(wrong_char)
                await HumanBehavior.random_delay_async(100, 300)
                await page.keyboard.press("Backspace")
                await HumanBehavior.random_delay_async(50, 150)
            
            await element.type(char)
            
            # Variable typing speed
            if char == ' ':
                await HumanBehavior.random_delay_async(50, 150)
            elif char in '.,!?;:':
                await HumanBehavior.random_delay_async(150, 300)
            else:
                await HumanBehavior.random_delay_async(30, 120)
        
        logger.debug(f"Typed {len(text)} characters with human-like timing")
    
    @staticmethod
    async def random_mouse_movement_async(page: Page) -> None:
        """Perform random mouse movements to appear active."""
        movements = random.randint(2, 4)
        for _ in range(movements):
            await HumanBehavior.mouse_move_async(page)
            await HumanBehavior.random_delay_async(500, 1500)
    
    @staticmethod
    async def pdf_viewing_behavior_async(page: Page) -> None:
        """Simulate human behavior when viewing a PDF."""
        logger.debug("Simulating PDF viewing behavior")
        
        # Initial load and orientation
        await HumanBehavior.random_delay_async(2000, 4000, "initial PDF load")
        
        # Scroll down a bit to "read" the first page
        await HumanBehavior.scroll_async(page, "down", random.randint(200, 400))
        await HumanBehavior.random_delay_async(3000, 5000, "reading first section")
        
        # Random mouse movement while "reading"
        await HumanBehavior.random_mouse_movement_async(page)
        
        # Scroll back up as if checking something
        await HumanBehavior.scroll_async(page, "up", random.randint(100, 200))
        await HumanBehavior.random_delay_async(1000, 2000, "checking header")
        
        # Move mouse to download area (typically top-right)
        viewport = page.viewport_size
        if viewport:
            await HumanBehavior.mouse_move_async(
                page, 
                viewport['width'] - random.randint(50, 150),
                random.randint(50, 150)
            )
        
        await HumanBehavior.random_delay_async(500, 1000, "locating download button")
    
    @staticmethod
    async def wait_for_download_async(page: Page) -> None:
        """Wait for download with human-like patience."""
        # Humans don't immediately close after clicking download
        await HumanBehavior.random_delay_async(1000, 2000, "waiting for download to start")
        
        # Might move mouse around while waiting
        if random.random() < 0.3:
            await HumanBehavior.random_mouse_movement_async(page)
    
    @staticmethod
    async def form_interaction_async(page: Page) -> None:
        """Simulate human interaction with forms."""
        # Look around the form first
        await HumanBehavior.random_delay_async(1000, 2000, "examining form")
        await HumanBehavior.scroll_async(page, "down", random.randint(100, 300))
        await HumanBehavior.random_delay_async(500, 1000)
        await HumanBehavior.scroll_async(page, "up", random.randint(100, 300))


# Example usage
if __name__ == "__main__":
    async def demo():
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            
            # Navigate with human behavior
            await page.goto("https://www.google.com")
            
            # Simulate human reading the page
            await HumanBehavior.reading_delay_async(500)
            
            # Random mouse movements
            await HumanBehavior.random_mouse_movement_async(page)
            
            # Type in search box
            search_box = await page.locator('input[name="q"]')
            if search_box:
                await HumanBehavior.type_text_async(
                    page,
                    selector='input[name="q"]',
                    text="test search query"
                )
            
            await browser.close()
    
    asyncio.run(demo())

# EOF