#!/usr/bin/env python3
"""
Visualize Scholar module dependencies using graphviz
"""

def create_dependency_graph():
    """Create a graphviz representation of Scholar module dependencies"""
    
    dot_content = """digraph scholar_dependencies {
    rankdir=BT;
    node [shape=box, style=rounded];
    
    // Define node styles
    node [fillcolor=lightblue, style="rounded,filled"];
    
    // Core data structures (Level 0)
    node [fillcolor=lightgreen];
    "_Paper.py";
    "_DOIResolver.py";
    
    // Service modules (Level 1)
    node [fillcolor=lightcoral];
    "_Papers.py";
    "_search.py";
    "_download.py";
    "_utils.py";
    "_enrichment.py";
    "_citation_enricher.py";
    "_scihub_downloader.py";
    "_BatchDOIResolver.py";
    "_core.py";
    
    // Orchestrator (Level 2)
    node [fillcolor=lightyellow];
    "_Scholar.py";
    
    // Entry point (Level 3)
    node [fillcolor=lightgray];
    "__init__.py";
    
    // Dependencies
    "_Papers.py" -> "_Paper.py";
    "_search.py" -> "_Paper.py";
    "_download.py" -> "_Paper.py";
    "_utils.py" -> "_Paper.py";
    "_utils.py" -> "_Papers.py";
    "_enrichment.py" -> "_Paper.py";
    "_citation_enricher.py" -> "_Paper.py";
    "_scihub_downloader.py" -> "_Paper.py";
    "_BatchDOIResolver.py" -> "_DOIResolver.py";
    "_core.py" -> "_Paper.py";
    "_core.py" -> "_Papers.py";
    
    "_Scholar.py" -> "_BatchDOIResolver.py";
    "_Scholar.py" -> "_Paper.py";
    "_Scholar.py" -> "_Papers.py";
    "_Scholar.py" -> "_DOIResolver.py";
    "_Scholar.py" -> "_download.py" [label="PDFManager"];
    "_Scholar.py" -> "_enrichment.py" [label="UnifiedEnricher"];
    "_Scholar.py" -> "_search.py" [label="UnifiedSearcher"];
    
    "__init__.py" -> "_Scholar.py" [label="Scholar, search, etc."];
    "__init__.py" -> "_Paper.py";
    "__init__.py" -> "_Papers.py";
    "__init__.py" -> "_utils.py";
    "__init__.py" -> "_citation_enricher.py";
    "__init__.py" -> "_scihub_downloader.py" [label="dois_to_local_pdfs"];
    
    // Create subgraphs for better visualization
    subgraph cluster_0 {
        label="Core Data Structures";
        style=filled;
        color=lightgrey;
        "_Paper.py";
        "_Papers.py";
    }
    
    subgraph cluster_1 {
        label="Resolution Services";
        style=filled;
        color=lightgrey;
        "_DOIResolver.py";
        "_BatchDOIResolver.py";
    }
    
    subgraph cluster_2 {
        label="Core Services";
        style=filled;
        color=lightgrey;
        "_search.py";
        "_download.py";
        "_enrichment.py";
        "_citation_enricher.py";
        "_scihub_downloader.py";
    }
}
"""
    
    # Save the dot file
    with open('/home/ywatanabe/proj/SciTeX-Code/scholar_dependencies.dot', 'w') as f:
        f.write(dot_content)
    
    print("Dependency graph saved to scholar_dependencies.dot")
    print("To generate an image, run:")
    print("  dot -Tpng scholar_dependencies.dot -o scholar_dependencies.png")
    print("  dot -Tsvg scholar_dependencies.dot -o scholar_dependencies.svg")

if __name__ == "__main__":
    create_dependency_graph()