<!-- ---
!-- Timestamp: 2025-07-29 04:11:55
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/open_url/ANTI_BOT_LOGICS.md
!-- --- -->

Of course. Yes, even with the stealth settings that disguise the browser's identity, the script's behavior can still be flagged as "bot-like." You're right to think about making it act more human, especially when running tasks in parallel.

## What Makes a Script "Bot-like"? 🤖
Websites use sophisticated heuristics to detect automated traffic. Beyond the browser's fingerprint, they look for behavioral patterns that are distinctly non-human:

Impossible Speed: Actions like clicking, navigating, and finding elements happen instantly, faster than any human could.

Perfect Predictability: The script always takes the exact same path and waits for fixed intervals (e.g., await page.wait_for_timeout(2000)). Humans are random.

No "Physical" Interaction: The script clicks elements without ever moving a mouse cursor over them. Humans almost always hover over a button before clicking it.

High Concurrency: A single IP address opening 5+ simultaneous sessions and rapidly firing requests is a massive red flag. A real person doesn't operate that way.

## How to Be More "Human" 🚶
Here are several ways to make your script's behavior more natural. You can implement these in layers, from simple to advanced.

1. Randomized Delays
Never use fixed waits. Humans are unpredictable. Replace fixed timeouts with a random wait within a reasonable range.

Where to change: _OpenURLResolver.py -> _follow_saml_redirect method.

What to change:

Python

import random

# In _follow_saml_redirect, replace this:
# await page.wait_for_timeout(2000)

# With this:
await page.wait_for_timeout(random.uniform(1500, 3000)) # Waits between 1.5 and 3.0 seconds
2. Simulate Mouse Movement
Before clicking an element, move the mouse over it first. This is a very strong signal of human interaction.

Where to change: _ResolverLinkFinder.py. It's best to create a small, reusable helper function.

What to change:

Python

# In _ResolverLinkFinder.py, you could add this helper
import random

async def _human_click(self, page: Page, selector: str):
    """Hovers over an element, waits a bit, then clicks."""
    element = await page.locator(selector).first
    if await element.is_visible():
        await element.hover()
        await page.wait_for_timeout(random.uniform(200, 500)) # Brief pause
        await element.click()
        return True
    return False

# Then, when you find a link to click, you would use this helper
# instead of a direct .click() call.
3. Control Concurrency (Most Important for Parallel Tasks) 🚦
This is the most effective fix for issues arising from parallel execution. Instead of launching all your tasks at once, use a semaphore to limit the number of tasks that can run at the same time (e.g., a maximum of 2 or 3).

Where to change: _OpenURLResolver.py -> resolve_dois_parallelly method.

What to change:

Python

# In _OpenURLResolver.py

import asyncio

class OpenURLResolver:
    # ... (other methods) ...

    async def resolve_dois_parallelly(self, dois: List[str], concurrency: int = 3) -> List[Optional[Dict[str, Any]]]:
        """
        Resolves a list of DOIs in parallel, with controlled concurrency.
        """
        if not dois:
            return []

        # Create a semaphore to limit concurrent tasks to the specified number
        semaphore = asyncio.Semaphore(concurrency)
        
        # Define a worker function that will be controlled by the semaphore
        async def worker(doi):
            async with semaphore:
                # This ensures only 'concurrency' number of workers can run this part at once
                return await self.resolve_async(doi=doi)

        logger.info(f"--- Starting parallel resolution for {len(dois)} DOIs (concurrency: {concurrency}) ---")
        
        # Create tasks using the worker function
        tasks = [worker(doi) for doi in dois]
        
        results = await asyncio.gather(*tasks)
        
        logger.info("--- Parallel resolution finished ---")
        return results
By adding a concurrency limit (a good default is 2 or 3), you dramatically reduce the chance of being flagged as a bot while still getting a significant speedup over sequential execution.

<!-- EOF -->