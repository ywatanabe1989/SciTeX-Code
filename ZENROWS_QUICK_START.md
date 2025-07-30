# ZenRows Scraping Browser Quick Start

## 1. Set Environment Variables

```bash
source .env.zenrows
```

Or manually export:
```bash
export SCITEX_SCHOLAR_BROWSER_BACKEND="zenrows"
export SCITEX_SCHOLAR_ZENROWS_API_KEY="822225799f9a4d847163f397ef86bb81b3f5ceb5"
export SCITEX_SCHOLAR_ZENROWS_PROXY_COUNTRY="au"
export SCITEX_SCHOLAR_2CAPTCHA_API_KEY="36d184fbba134f828cdd314f01dc7f18"
```

## 2. Quick Test

```python
from scitex.scholar import Scholar, ScholarConfig

# Configure for ZenRows
config = ScholarConfig(
    browser_backend="zenrows",
    zenrows_proxy_country="au"
)

# Use normally
scholar = Scholar(config=config)
papers = await scholar.search("10.1038/s41586-023-06516-4")
```

## 3. Run Examples

```bash
# Basic test
python examples/scholar/test_zenrows_integration.py

# Full example
python examples/scholar/zenrows_usage_example.py
```

That's it! The ZenRows backend handles all the complexity of running a remote browser session.