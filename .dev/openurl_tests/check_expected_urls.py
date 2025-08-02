#!/usr/bin/env python
"""Check expected publisher URLs for DOIs."""

# DOI to publisher URL mapping
doi_info = {
    "10.1002/hipo.22488": {
        "title": "Hippocampal sharp wave-ripple: A cognitive biomarker",
        "journal": "Hippocampus",
        "publisher": "Wiley",
        "expected_url": "https://onlinelibrary.wiley.com/doi/10.1002/hipo.22488"
    },
    "10.1038/nature12373": {
        "title": "Discrete global grid systems",
        "journal": "Nature", 
        "publisher": "Nature Publishing Group",
        "expected_url": "https://www.nature.com/articles/nature12373"
    },
    "10.1016/j.neuron.2018.01.048": {
        "title": "Neuron article",
        "journal": "Neuron",
        "publisher": "Cell Press/Elsevier",
        "expected_url": "https://www.cell.com/neuron/fulltext/S0896-6273(18)30048-5"
    },
    "10.1126/science.1172133": {
        "title": "A general framework for analyzing sustainability",
        "journal": "Science",
        "publisher": "AAAS",
        "expected_url": "https://www.science.org/doi/10.1126/science.1172133"
    },
    "10.1073/pnas.0608765104": {
        "title": "PNAS article",
        "journal": "PNAS",
        "publisher": "National Academy of Sciences",
        "expected_url": "https://www.pnas.org/doi/10.1073/pnas.0608765104"
    }
}

print("Expected Publisher URLs for DOIs:\n")
print("="*80)

for doi, info in doi_info.items():
    print(f"\nDOI: {doi}")
    print(f"Journal: {info['journal']} ({info['publisher']})")
    print(f"Expected URL: {info['expected_url']}")

print("\n" + "="*80)
print("\nNOTE: These are the URLs you should reach after successful authentication.")
print("\nCurrent status:")
print("❌ Without authentication: You get stuck at SSO/OpenAthens login pages")
print("✅ With authentication: The resolver should redirect to these publisher URLs")
print("\nTo authenticate, run:")
print("  await auth_manager.authenticate()")
print("in your IPython session first.")