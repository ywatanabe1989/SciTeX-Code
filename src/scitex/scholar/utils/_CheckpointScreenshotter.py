#!/usr/bin/env python3
"""
Checkpoint Screenshotter

Utility for taking indexed/timestamped screenshots at each step of the PDF detection
process to track what's happening in relative time sequence.

Optimized for debugging with lower resolution and automatic indexing.
"""

import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class CheckpointScreenshotter:
    """
    Takes systematic screenshots at checkpoints for debugging and monitoring.
    
    Features:
    - Automatic indexing (01, 02, 03...)
    - Timestamp in filenames  
    - Lower resolution for efficiency
    - Step descriptions
    - Organized directory structure
    """
    
    def __init__(self, base_dir: Path, session_name: str = "session"):
        """
        Initialize checkpoint screenshotter.
        
        Args:
            base_dir: Base directory for screenshots
            session_name: Name for this session (e.g., "science_test", "nature_test")
        """
        self.session_name = session_name
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create session directory
        self.session_dir = base_dir / f"checkpoints_{session_name}_{self.timestamp}"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize counters
        self.checkpoint_counter = 0
        self.error_counter = 0
        
        # Screenshot settings (optimized for debugging)
        self.screenshot_options = {
            'full_page': False,  # Viewport only for speed
            'quality': 60,       # Lower quality for smaller files
            'type': 'jpeg'       # JPEG for better compression
        }
        
        logger.info(f"📸 Checkpoint Screenshotter initialized: {self.session_dir}")
    
    async def checkpoint(self, page, description: str, full_page: bool = False) -> str:
        """
        Take a checkpoint screenshot.
        
        Args:
            page: Playwright page object
            description: Description of what this checkpoint shows
            full_page: Whether to capture full page (default: viewport only)
            
        Returns:
            Path to the screenshot file
        """
        self.checkpoint_counter += 1
        
        # Generate filename with index, timestamp, and description
        timestamp_short = datetime.now().strftime("%H%M%S")
        safe_description = "".join(c for c in description if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_description = safe_description.replace(' ', '_').lower()[:30]  # Max 30 chars
        
        filename = f"cp{self.checkpoint_counter:02d}_{timestamp_short}_{safe_description}.jpg"
        filepath = self.session_dir / filename
        
        try:
            # Take screenshot with optimized settings
            await page.screenshot(
                path=str(filepath),
                full_page=full_page,
                quality=self.screenshot_options['quality'],
                type=self.screenshot_options['type']
            )
            
            file_size = filepath.stat().st_size / 1024  # KB
            logger.info(f"📸 Checkpoint {self.checkpoint_counter:02d}: {description} ({file_size:.1f} KB)")
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to take checkpoint screenshot: {e}")
            return ""
    
    async def error_checkpoint(self, page, error_description: str, full_page: bool = True) -> str:
        """
        Take an error screenshot with full context.
        
        Args:
            page: Playwright page object
            error_description: Description of the error
            full_page: Whether to capture full page (default: True for errors)
            
        Returns:
            Path to the screenshot file
        """
        self.error_counter += 1
        
        timestamp_short = datetime.now().strftime("%H%M%S")
        safe_description = "".join(c for c in error_description if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_description = safe_description.replace(' ', '_').lower()[:30]
        
        filename = f"ERROR_{self.error_counter:02d}_{timestamp_short}_{safe_description}.jpg"
        filepath = self.session_dir / filename
        
        try:
            await page.screenshot(
                path=str(filepath),
                full_page=full_page,
                quality=80,  # Higher quality for error analysis
                type='jpeg'
            )
            
            file_size = filepath.stat().st_size / 1024
            logger.warning(f"🚨 Error checkpoint {self.error_counter:02d}: {error_description} ({file_size:.1f} KB)")
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to take error screenshot: {e}")
            return ""
    
    async def page_info_checkpoint(self, page, step_description: str) -> dict:
        """
        Take screenshot + capture page info for comprehensive checkpoint.
        
        Args:
            page: Playwright page object
            step_description: Description of this step
            
        Returns:
            Dictionary with screenshot path and page info
        """
        # Take screenshot
        screenshot_path = await self.checkpoint(page, step_description)
        
        # Capture page information
        try:
            page_info = await page.evaluate('''
                () => {
                    return {
                        url: window.location.href,
                        title: document.title,
                        ready_state: document.readyState,
                        has_content: document.body ? document.body.textContent.length > 100 : false,
                        timestamp: new Date().toISOString()
                    };
                }
            ''')
        except Exception as e:
            page_info = {
                'url': 'unknown',
                'title': 'unknown', 
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
        
        # Log the info
        logger.info(f"📊 Page info: {page_info.get('title', 'No title')[:50]}...")
        logger.info(f"🔗 URL: {page_info.get('url', 'unknown')[:80]}...")
        
        return {
            'screenshot_path': screenshot_path,
            'page_info': page_info,
            'step_description': step_description,
            'checkpoint_number': self.checkpoint_counter
        }
    
    def create_session_report(self) -> str:
        """Create a summary report of the session."""
        report_path = self.session_dir / "session_report.md"
        
        # List all screenshots
        screenshots = sorted(self.session_dir.glob("*.jpg"))
        
        report_content = f"""# Checkpoint Session Report

**Session:** {self.session_name}
**Timestamp:** {self.timestamp}
**Directory:** {self.session_dir}

## Screenshots Captured

**Total Checkpoints:** {self.checkpoint_counter}
**Total Errors:** {self.error_counter}
**Total Screenshots:** {len(screenshots)}

### Screenshot Timeline

"""
        
        for screenshot in screenshots:
            file_size = screenshot.stat().st_size / 1024
            report_content += f"- `{screenshot.name}` ({file_size:.1f} KB)\n"
        
        report_content += f"""

## Usage

These screenshots provide a time-sequenced view of the PDF detection process:

1. **Checkpoints (cp01, cp02, ...)**: Normal progression through steps
2. **Errors (ERROR_01, ERROR_02, ...)**: Issues encountered during processing  
3. **Timestamps**: Each filename includes HHMMSS timestamp for time sequencing
4. **Descriptions**: Filenames include step descriptions for easy identification

## Analysis

Use these screenshots to:
- Debug failed PDF detections on different journals
- Compare working vs non-working publisher workflows  
- Identify where bot detection or authentication issues occur
- Track the progression of browser state changes

Generated by CheckpointScreenshotter on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        with open(report_path, 'w') as f:
            f.write(report_content)
        
        logger.info(f"📋 Session report created: {report_path}")
        return str(report_path)
    
    def get_session_summary(self) -> dict:
        """Get summary information about this session."""
        screenshots = list(self.session_dir.glob("*.jpg"))
        total_size = sum(s.stat().st_size for s in screenshots) / (1024 * 1024)  # MB
        
        return {
            'session_name': self.session_name,
            'session_dir': str(self.session_dir),
            'timestamp': self.timestamp,
            'checkpoints': self.checkpoint_counter,
            'errors': self.error_counter,
            'total_screenshots': len(screenshots),
            'total_size_mb': round(total_size, 2),
            'screenshots': [s.name for s in sorted(screenshots)]
        }


# Convenience functions
async def take_checkpoint(screenshotter: CheckpointScreenshotter, page, description: str) -> str:
    """Convenience function to take a checkpoint screenshot."""
    return await screenshotter.checkpoint(page, description)


async def take_error_checkpoint(screenshotter: CheckpointScreenshotter, page, error_desc: str) -> str:
    """Convenience function to take an error screenshot."""
    return await screenshotter.error_checkpoint(page, error_desc)


async def take_info_checkpoint(screenshotter: CheckpointScreenshotter, page, description: str) -> dict:
    """Convenience function to take a checkpoint with page info."""
    return await screenshotter.page_info_checkpoint(page, description)