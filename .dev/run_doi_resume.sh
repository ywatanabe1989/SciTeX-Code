#!/bin/bash
# Resume DOI resolution

echo "Resuming DOI resolution..."
echo "This will continue from where it left off"
echo "="*60

python -m scitex.scholar.resolve_dois \
    --bibtex src/scitex/scholar/docs/papers.bib \
    --resume \
    --output .dev/resolved_dois_complete.json \
    --verbose

echo ""
echo "="*60
echo "DOI resolution completed!"