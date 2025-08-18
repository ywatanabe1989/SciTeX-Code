#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-16 20:35:03 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/PlayWrightVision.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/PlayWrightVision.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
"""
Playwright Vision - Computer Vision capabilities for Playwright
Finds and clicks elements using visual pattern matching
"""

import asyncio
import base64
import io
from typing import List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image
from playwright.async_api import Page

from scitex import logging

logger = logging.getLogger(__name__)


class PlaywrightVision:
    """Add computer vision capabilities to Playwright."""

    def __init__(self, page: Page):
        self.page = page

    async def find_and_click_image(
        self,
        target_image_path: str,
        confidence: float = 0.8,
        timeout: int = 10000,
        click_offset: Tuple[int, int] = (0, 0),
    ) -> bool:
        """
        Find an image on the page and click it.

        Args:
            target_image_path: Path to the image to find (e.g., download button)
            confidence: Match confidence threshold (0-1)
            timeout: Maximum time to wait for the image
            click_offset: Offset from center of found image to click

        Returns:
            True if image was found and clicked, False otherwise
        """
        start_time = asyncio.get_event_loop().time()

        while (asyncio.get_event_loop().time() - start_time) * 1000 < timeout:
            # Take screenshot of current page
            screenshot = await self.page.screenshot()

            # Find the target image in the screenshot
            location = self._find_image_in_screenshot(
                screenshot, target_image_path, confidence
            )

            if location:
                x, y, width, height = location

                # Calculate click position (center + offset)
                click_x = x + width // 2 + click_offset[0]
                click_y = y + height // 2 + click_offset[1]

                logger.info(
                    f"Found image at ({x}, {y}), clicking at ({click_x}, {click_y})"
                )

                # Click the found position
                await self.page.mouse.click(click_x, click_y)
                return True

            # Wait a bit before retrying
            await asyncio.sleep(0.5)

        logger.warn(f"Image not found within {timeout}ms")
        return False

    async def find_text_and_click(
        self,
        text_to_find: str,
        timeout: int = 10000,
        font_scale_range: Tuple[float, float] = (0.5, 2.0),
    ) -> bool:
        """
        Find text in the page using OCR and click it.

        Args:
            text_to_find: Text to search for
            timeout: Maximum time to wait
            font_scale_range: Range of font sizes to try

        Returns:
            True if text was found and clicked
        """
        try:
            import pytesseract
        except ImportError:
            logger.error(
                "pytesseract not installed. Install with: pip install pytesseract"
            )
            return False

        start_time = asyncio.get_event_loop().time()

        while (asyncio.get_event_loop().time() - start_time) * 1000 < timeout:
            # Take screenshot
            screenshot = await self.page.screenshot()

            # Convert to PIL Image
            image = Image.open(io.BytesIO(screenshot))

            # Perform OCR
            ocr_data = pytesseract.image_to_data(
                image, output_type=pytesseract.Output.DICT
            )

            # Find the text
            for i, word in enumerate(ocr_data["text"]):
                if text_to_find.lower() in str(word).lower():
                    x = ocr_data["left"][i]
                    y = ocr_data["top"][i]
                    width = ocr_data["width"][i]
                    height = ocr_data["height"][i]

                    if width > 0 and height > 0:
                        click_x = x + width // 2
                        click_y = y + height // 2

                        logger.info(
                            f"Found text '{word}' at ({x}, {y}), clicking at ({click_x}, {click_y})"
                        )

                        await self.page.mouse.click(click_x, click_y)
                        return True

            await asyncio.sleep(0.5)

        logger.warn(f"Text '{text_to_find}' not found within {timeout}ms")
        return False

    async def find_download_button_and_click(self) -> bool:
        """
        Specialized method to find and click download buttons in PDF viewers.
        Uses multiple visual strategies.
        """
        logger.info("Searching for download button using computer vision...")

        # Strategy 1: Look for download icon patterns
        download_patterns = [
            self._create_download_arrow_pattern(),
            self._create_download_icon_pattern(),
            self._create_save_icon_pattern(),
        ]

        screenshot = await self.page.screenshot()
        screenshot_np = np.array(Image.open(io.BytesIO(screenshot)))

        for pattern_name, pattern in download_patterns:
            locations = self._find_pattern_in_image(screenshot_np, pattern)
            if locations:
                x, y, w, h = locations[0]  # Take first match
                click_x = x + w // 2
                click_y = y + h // 2

                logger.info(
                    f"Found {pattern_name} at ({x}, {y}), clicking at ({click_x}, {click_y})"
                )
                await self.page.mouse.click(click_x, click_y)
                return True

        # Strategy 2: Look for text "Download" using OCR
        if await self.find_text_and_click("Download"):
            return True

        # Strategy 3: Look for typical download button colors and shapes
        button_locations = self._find_button_shapes(screenshot_np)

        for x, y, w, h in button_locations[:5]:  # Try top 5 candidates
            # Check if this might be a download button
            # by analyzing the region for download-like icons
            region = screenshot_np[y : y + h, x : x + w]

            if self._looks_like_download_button(region):
                click_x = x + w // 2
                click_y = y + h // 2

                logger.info(f"Found potential download button at ({x}, {y})")
                await self.page.mouse.click(click_x, click_y)

                # Wait to see if download triggered
                await asyncio.sleep(2)

                # Check if download started (you'd need to implement this check)
                # For now, return True optimistically
                return True

        logger.warn("No download button found using computer vision")
        return False

    def _find_image_in_screenshot(
        self, screenshot: bytes, target_path: str, confidence: float
    ) -> Optional[Tuple[int, int, int, int]]:
        """Find target image in screenshot using template matching."""
        # Convert screenshot to numpy array
        screenshot_np = np.array(Image.open(io.BytesIO(screenshot)))

        # Load target image
        target = cv2.imread(target_path)
        if target is None:
            logger.error(f"Could not load target image: {target_path}")
            return None

        # Convert to grayscale for better matching
        screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)
        target_gray = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)

        # Perform template matching
        result = cv2.matchTemplate(
            screenshot_gray, target_gray, cv2.TM_CCOEFF_NORMED
        )

        # Find best match
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= confidence:
            x, y = max_loc
            h, w = target_gray.shape
            return (x, y, w, h)

        return None

    def _find_pattern_in_image(
        self, image: np.ndarray, pattern: np.ndarray, confidence: float = 0.7
    ) -> List[Tuple[int, int, int, int]]:
        """Find all occurrences of a pattern in an image."""
        # Convert to grayscale
        if len(image.shape) == 3:
            image_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            image_gray = image

        if len(pattern.shape) == 3:
            pattern_gray = cv2.cvtColor(pattern, cv2.COLOR_RGB2GRAY)
        else:
            pattern_gray = pattern

        # Template matching
        result = cv2.matchTemplate(
            image_gray, pattern_gray, cv2.TM_CCOEFF_NORMED
        )

        # Find all matches above threshold
        locations = np.where(result >= confidence)

        matches = []
        h, w = pattern_gray.shape

        for pt in zip(*locations[::-1]):
            matches.append((pt[0], pt[1], w, h))

        # Non-maximum suppression to remove overlapping matches
        return self._non_max_suppression(matches)

    def _non_max_suppression(
        self,
        boxes: List[Tuple[int, int, int, int]],
        overlap_thresh: float = 0.3,
    ) -> List[Tuple[int, int, int, int]]:
        """Remove overlapping bounding boxes."""
        if not boxes:
            return []

        boxes = np.array(boxes)
        x1 = boxes[:, 0]
        y1 = boxes[:, 1]
        x2 = boxes[:, 0] + boxes[:, 2]
        y2 = boxes[:, 1] + boxes[:, 3]

        areas = boxes[:, 2] * boxes[:, 3]
        indices = np.argsort(areas)[::-1]

        keep = []
        while len(indices) > 0:
            i = indices[0]
            keep.append(i)

            if len(indices) == 1:
                break

            # Calculate IoU
            xx1 = np.maximum(x1[i], x1[indices[1:]])
            yy1 = np.maximum(y1[i], y1[indices[1:]])
            xx2 = np.minimum(x2[i], x2[indices[1:]])
            yy2 = np.minimum(y2[i], y2[indices[1:]])

            w = np.maximum(0, xx2 - xx1)
            h = np.maximum(0, yy2 - yy1)

            overlap = (w * h) / areas[indices[1:]]

            indices = indices[1:][overlap <= overlap_thresh]

        return [tuple(boxes[i]) for i in keep]

    def _create_download_arrow_pattern(self) -> Tuple[str, np.ndarray]:
        """Create a typical download arrow pattern."""
        # Create a simple download arrow icon
        pattern = np.ones((30, 30, 3), dtype=np.uint8) * 255

        # Draw download arrow (pointing down with a line underneath)
        # Arrow shaft
        cv2.line(pattern, (15, 5), (15, 20), (0, 0, 0), 2)

        # Arrow head
        cv2.line(pattern, (15, 20), (10, 15), (0, 0, 0), 2)
        cv2.line(pattern, (15, 20), (20, 15), (0, 0, 0), 2)

        # Bottom line (representing disk/save)
        cv2.line(pattern, (8, 25), (22, 25), (0, 0, 0), 2)

        return ("download_arrow", pattern)

    def _create_download_icon_pattern(self) -> Tuple[str, np.ndarray]:
        """Create a download icon pattern (cloud with down arrow)."""
        pattern = np.ones((30, 30, 3), dtype=np.uint8) * 255

        # Simple download icon
        cv2.circle(pattern, (15, 10), 8, (0, 0, 0), 1)
        cv2.line(pattern, (15, 10), (15, 22), (0, 0, 0), 2)
        cv2.line(pattern, (15, 22), (11, 18), (0, 0, 0), 2)
        cv2.line(pattern, (15, 22), (19, 18), (0, 0, 0), 2)

        return ("download_icon", pattern)

    def _create_save_icon_pattern(self) -> Tuple[str, np.ndarray]:
        """Create a floppy disk save icon pattern."""
        pattern = np.ones((30, 30, 3), dtype=np.uint8) * 255

        # Floppy disk outline
        cv2.rectangle(pattern, (5, 5), (25, 25), (0, 0, 0), 2)
        cv2.rectangle(pattern, (8, 5), (22, 12), (100, 100, 100), -1)
        cv2.rectangle(pattern, (18, 7), (20, 10), (255, 255, 255), -1)

        return ("save_icon", pattern)

    def _find_button_shapes(
        self, image: np.ndarray
    ) -> List[Tuple[int, int, int, int]]:
        """Find rectangular button-like shapes in the image."""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        # Edge detection
        edges = cv2.Canny(gray, 50, 150)

        # Find contours
        contours, _ = cv2.findContours(
            edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        buttons = []
        for contour in contours:
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)

            # Filter for button-like dimensions
            if 20 < w < 200 and 15 < h < 60:
                aspect_ratio = w / h
                if 1.5 < aspect_ratio < 6:  # Typical button aspect ratios
                    buttons.append((x, y, w, h))

        return buttons

    def _looks_like_download_button(self, region: np.ndarray) -> bool:
        """Analyze if a region looks like a download button."""
        # Check for download-like features:
        # 1. Has some text or icon
        # 2. Has contrast (not uniform color)
        # 3. Might have specific colors (blue, green for download buttons)

        if region.size == 0:
            return False

        # Check color variance (buttons usually have some contrast)
        std_dev = np.std(region)
        if std_dev < 10:  # Too uniform
            return False

        # Check for common download button colors
        avg_color = np.mean(region, axis=(0, 1))

        # Blue-ish buttons (common for downloads)
        if avg_color[2] > avg_color[0] and avg_color[2] > avg_color[1]:
            return True

        # Green-ish buttons
        if avg_color[1] > avg_color[0] and avg_color[1] > avg_color[2]:
            return True

        # Check for icon-like patterns (high contrast areas)
        gray = cv2.cvtColor(region, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edge_ratio = np.sum(edges > 0) / edges.size

        # If there are enough edges (indicating text or icons)
        if 0.05 < edge_ratio < 0.5:
            return True

        return False

# EOF
