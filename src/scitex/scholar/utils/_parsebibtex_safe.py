#!/usr/bin/env python3

def parsebibtex_safe(bibtex_path):
    """Safely parse BibTeX file, handling comment lines."""
    from pathlib import Path
    import re
    
    with open(bibtex_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove comment lines starting with %
    lines = content.split('\n')
    cleaned_lines = [line for line in lines if not re.match(r'^\s*%', line)]
    cleaned_content = '\n'.join(cleaned_lines)
    
    # Try standard parser first
    try:
        import bibtexparser
        bib_db = bibtexparser.loads(cleaned_content)
        if len(bib_db.entries) > 0:
            return bib_db.entries
    except:
        pass
    
    # Manual parsing fallback
    entries = []
    pattern = r'@(article|inproceedings|book)\s*\{\s*([^,\s]+)\s*,(.*?)(?=\n@|\Z)'
    matches = re.findall(pattern, cleaned_content, re.DOTALL | re.IGNORECASE)
    
    for entry_type, entry_id, entry_content in matches:
        entry = {'ENTRYTYPE': entry_type.lower(), 'ID': entry_id.strip()}
        
        # Parse fields
        field_pattern = r'(\w+)\s*=\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
        field_matches = re.findall(field_pattern, entry_content)
        
        for field_name, field_value in field_matches:
            if not field_name.endswith('_source'):
                entry[field_name.lower()] = field_value.strip()
        
        if entry.get('title') or entry.get('doi'):
            entries.append(entry)
    
    return entries