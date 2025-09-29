#!/usr/bin/env python3
"""Generate simple HTML dashboard without IEEE special handling."""

import json
from pathlib import Path
import webbrowser

def generate_simple_dashboard():
    """Generate HTML dashboard treating all papers equally."""
    
    pac_dir = Path.home() / '.scitex/scholar/library/pac'
    papers_data = []
    
    # Collect paper data
    for item in sorted(pac_dir.iterdir()):
        if item.is_symlink():
            target = item.resolve()
            if target.exists():
                pdfs = list(target.glob('*.pdf'))
                has_pdf = len(pdfs) > 0
                
                metadata_file = target / 'metadata.json'
                if metadata_file.exists():
                    with open(metadata_file) as f:
                        metadata = json.load(f)
                    
                    paper_info = {
                        'name': item.name,
                        'journal': metadata.get('journal', ''),
                        'doi': metadata.get('doi', ''),
                        'title': metadata.get('title', ''),
                        'has_pdf': has_pdf,
                        'id': item.name.replace('-', '_')
                    }
                else:
                    paper_info = {
                        'name': item.name,
                        'journal': '',
                        'doi': '',
                        'title': item.name,
                        'has_pdf': has_pdf,
                        'id': item.name.replace('-', '_')
                    }
                
                papers_data.append(paper_info)
    
    # Generate complete HTML
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PAC Collection - PDF Download Dashboard</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #4CAF50;
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
        .controls {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 20px 0;
        }}
        button {{
            background: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin: 5px;
        }}
        button:hover {{
            background: #45a049;
        }}
        button.secondary {{
            background: #2196F3;
        }}
        button.secondary:hover {{
            background: #1976D2;
        }}
        button.warning {{
            background: #ff9800;
        }}
        button.warning:hover {{
            background: #f57c00;
        }}
        .paper-grid {{
            display: grid;
            gap: 10px;
            margin-top: 20px;
        }}
        .paper-card {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            display: grid;
            grid-template-columns: 30px 30px 1fr 100px;
            align-items: center;
            gap: 15px;
        }}
        .paper-card.has-pdf {{
            background: #e8f5e9;
        }}
        .paper-card.no-pdf {{
            background: #fff3e0;
        }}
        .status-icon {{
            font-size: 20px;
            text-align: center;
        }}
        .paper-info {{
            flex-grow: 1;
        }}
        .paper-title {{
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }}
        .paper-journal {{
            color: #666;
            font-size: 14px;
        }}
        .paper-doi {{
            color: #999;
            font-size: 12px;
            margin-top: 3px;
        }}
        .paper-actions {{
            text-align: right;
        }}
        .paper-actions a {{
            color: #2196F3;
            text-decoration: none;
            padding: 5px 10px;
            border: 1px solid #2196F3;
            border-radius: 3px;
            font-size: 14px;
            display: inline-block;
        }}
        .paper-actions a:hover {{
            background: #2196F3;
            color: white;
        }}
        .filter-tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }}
        .filter-tab {{
            padding: 8px 16px;
            background: #e0e0e0;
            border-radius: 5px;
            cursor: pointer;
        }}
        .filter-tab.active {{
            background: #4CAF50;
            color: white;
        }}
        #selected-count {{
            margin-left: 20px;
            color: #666;
        }}
        input[type="checkbox"] {{
            width: 20px;
            height: 20px;
            cursor: pointer;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 PAC Collection - PDF Download Dashboard</h1>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number" id="pdf-count">0</div>
                <div class="stat-label">PDFs Downloaded</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="missing-count">0</div>
                <div class="stat-label">Missing PDFs</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="total-count">0</div>
                <div class="stat-label">Total Papers</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="coverage">0%</div>
                <div class="stat-label">Coverage</div>
            </div>
        </div>

        <div class="controls">
            <h3>🎮 Batch Actions</h3>
            <button onclick="selectAll()">Select All Missing</button>
            <button onclick="selectNone()">Clear Selection</button>
            <button class="secondary" onclick="openSelected()">Open Selected in Tabs</button>
            <button class="warning" onclick="openSelectedBatch(5)">Open in Batches (5)</button>
            <span id="selected-count">0 selected</span>
            
            <div class="filter-tabs" style="margin-top: 20px;">
                <div class="filter-tab active" onclick="filterPapers('all', event)">All Papers</div>
                <div class="filter-tab" onclick="filterPapers('missing', event)">Missing PDFs</div>
                <div class="filter-tab" onclick="filterPapers('has-pdf', event)">Has PDF</div>
            </div>
        </div>

        <div id="paper-grid" class="paper-grid">
            <!-- Papers will be inserted here -->
        </div>
    </div>

    <script>
        // Embedded paper data
        const papers = {json.dumps(papers_data, indent=2)};
        
        let currentFilter = 'all';

        function updateStats() {{
            const withPdf = papers.filter(p => p.has_pdf).length;
            const missing = papers.filter(p => !p.has_pdf).length;
            const total = papers.length;
            const coverage = Math.round((withPdf / total) * 100);

            document.getElementById('pdf-count').textContent = withPdf;
            document.getElementById('missing-count').textContent = missing;
            document.getElementById('total-count').textContent = total;
            document.getElementById('coverage').textContent = coverage + '%';
        }}

        function renderPapers() {{
            const grid = document.getElementById('paper-grid');
            let filteredPapers = papers;

            if (currentFilter === 'missing') {{
                filteredPapers = papers.filter(p => !p.has_pdf);
            }} else if (currentFilter === 'has-pdf') {{
                filteredPapers = papers.filter(p => p.has_pdf);
            }}

            grid.innerHTML = filteredPapers.map((paper, index) => {{
                const cardClass = paper.has_pdf ? 'has-pdf' : 'no-pdf';
                const icon = paper.has_pdf ? '✅' : '❌';
                const checkboxId = 'cb_' + index + '_' + (paper.id || index);
                const checkbox = !paper.has_pdf ? 
                    `<input type="checkbox" class="paper-checkbox" id="${{checkboxId}}" data-doi="${{paper.doi || ''}}" data-name="${{paper.name}}">` : 
                    '<span></span>';

                return `
                    <div class="paper-card ${{cardClass}}">
                        ${{checkbox}}
                        <div class="status-icon">${{icon}}</div>
                        <div class="paper-info">
                            <div class="paper-title">${{paper.name}}</div>
                            <div class="paper-journal">${{paper.journal || 'Unknown Journal'}}</div>
                            <div class="paper-doi">DOI: ${{paper.doi || 'N/A'}}</div>
                        </div>
                        <div class="paper-actions">
                            ${{paper.doi && paper.doi !== '' ? `<a href="https://doi.org/${{paper.doi}}" target="_blank">Open DOI</a>` : ''}}
                        </div>
                    </div>
                `;
            }}).join('');

            updateSelectedCount();
        }}

        function filterPapers(filter, event) {{
            currentFilter = filter;
            document.querySelectorAll('.filter-tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            event.target.classList.add('active');
            renderPapers();
        }}

        function selectAll() {{
            document.querySelectorAll('.paper-checkbox').forEach(cb => {{
                cb.checked = true;
            }});
            updateSelectedCount();
        }}

        function selectNone() {{
            document.querySelectorAll('.paper-checkbox').forEach(cb => {{
                cb.checked = false;
            }});
            updateSelectedCount();
        }}

        function updateSelectedCount() {{
            const checkboxes = document.querySelectorAll('.paper-checkbox:checked');
            document.getElementById('selected-count').textContent = `${{checkboxes.length}} selected`;
        }}

        function getSelectedDOIs() {{
            const selected = [];
            const selectedInfo = [];
            document.querySelectorAll('.paper-checkbox:checked').forEach(cb => {{
                const doi = cb.dataset.doi;
                const name = cb.dataset.name;
                if (doi && doi !== '' && doi !== 'None') {{
                    selected.push({{doi: doi, name: name}});
                }} else {{
                    selectedInfo.push(name + ' (no DOI)');
                }}
            }});
            
            if (selectedInfo.length > 0) {{
                console.log('Papers without DOIs:', selectedInfo);
            }}
            
            return selected;
        }}

        function openSelected() {{
            const selected = getSelectedDOIs();
            if (selected.length === 0) {{
                alert('No papers with valid DOIs selected. Some papers may not have DOI entries.');
                return;
            }}
            if (selected.length > 20) {{
                if (!confirm(`This will open ${{selected.length}} tabs. Continue?`)) {{
                    return;
                }}
            }}
            selected.forEach(item => {{
                window.open(`https://doi.org/${{item.doi}}`, '_blank');
            }});
        }}

        function openSelectedBatch(batchSize = 5) {{
            const selected = getSelectedDOIs();
            if (selected.length === 0) {{
                alert('No papers with valid DOIs selected. Some papers may not have DOI entries.');
                return;
            }}

            let currentBatch = 0;
            
            function openNextBatch() {{
                const start = currentBatch * batchSize;
                const end = Math.min(start + batchSize, selected.length);
                
                if (start >= selected.length) {{
                    alert('All batches opened!');
                    return;
                }}

                console.log(`Opening batch ${{currentBatch + 1}}: papers ${{start + 1}} to ${{end}}`);
                
                for (let i = start; i < end; i++) {{
                    console.log(`Opening: ${{selected[i].name}}`);
                    window.open(`https://doi.org/${{selected[i].doi}}`, '_blank');
                }}

                currentBatch++;
                
                if (end < selected.length) {{
                    setTimeout(() => {{
                        if (confirm(`Batch ${{currentBatch}} opened. Open next batch (${{Math.min(batchSize, selected.length - end)}} papers)?`)) {{
                            openNextBatch();
                        }}
                    }}, 2000);
                }}
            }}

            openNextBatch();
        }}

        // Event listener for checkboxes
        document.addEventListener('change', (e) => {{
            if (e.target.classList.contains('paper-checkbox')) {{
                updateSelectedCount();
            }}
        }});

        // Initialize on page load
        console.log(`Loaded ${{papers.length}} papers`);
        updateStats();
        renderPapers();
    </script>
</body>
</html>"""
    
    # Save complete HTML
    output_file = Path('.dev_pac/pac_dashboard_simple.html')
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    # Calculate stats
    total = len(papers_data)
    with_pdf = sum(1 for p in papers_data if p['has_pdf'])
    missing = total - with_pdf
    coverage = (with_pdf / total * 100) if total > 0 else 0
    
    print("="*80)
    print("SIMPLE DASHBOARD GENERATED")
    print("="*80)
    print(f"\n📊 Statistics:")
    print(f"  Total papers: {total}")
    print(f"  With PDFs: {with_pdf} ✅")
    print(f"  Missing PDFs: {missing} ❌")
    print(f"  Coverage: {coverage:.1f}%")
    
    # List papers without DOIs
    no_doi = [p for p in papers_data if not p.get('doi') and not p['has_pdf']]
    if no_doi:
        print(f"\n⚠️  Papers without DOIs ({len(no_doi)}):")
        for p in no_doi:
            print(f"  • {p['name']}")
    
    print(f"\n📁 Dashboard: {output_file.absolute()}")
    
    # Open in browser
    webbrowser.open(f'file://{output_file.absolute()}')
    
    print(f"\n💡 Usage:")
    print(f"  1. Click 'Missing PDFs' tab to see papers without PDFs")
    print(f"  2. Click 'Select All Missing' to select them")
    print(f"  3. Click 'Open in Batches' to open 5 at a time")
    print(f"  4. Save PDFs manually when they open")

if __name__ == "__main__":
    generate_simple_dashboard()