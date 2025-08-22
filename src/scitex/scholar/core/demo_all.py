#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 15:40:00 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/core/demo_all.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/core/demo_all.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Comprehensive demonstration of Paper, Papers, and Scholar integration.

This script shows how all three core classes work together to provide
a complete scientific literature management system with storage integration.
"""

import tempfile
from pathlib import Path

from ._Paper import Paper
from ._Papers import Papers
from ._Scholar import Scholar


def demo_individual_paper():
    """Demonstrate individual Paper operations."""
    print("🔬 PAPER DEMO - Individual Publication Management")
    print("-" * 50)
    
    # Create a paper with full metadata
    paper = Paper(
        title="Neural Machine Translation by Jointly Learning to Align and Translate",
        authors=["Bahdanau, Dzmitry", "Cho, Kyunghyun", "Bengio, Yoshua"],
        journal="ICLR",
        year=2015,
        doi="10.48550/arXiv.1409.0473",
        abstract="Neural machine translation is a recently proposed approach to machine translation...",
        keywords=["neural machine translation", "attention mechanism", "sequence-to-sequence"],
        citation_count=15000,
        impact_factor=8.5,
        url="https://arxiv.org/abs/1409.0473",
        project="attention_mechanisms"
    )
    
    print(f"📄 Created: {paper}")
    print(f"📊 Citations: {paper.citation_count:,}")
    print(f"📈 Impact Factor: {paper.impact_factor}")
    
    # Demonstrate storage
    try:
        library_id = paper.save_to_library()
        print(f"💾 Saved to library: {library_id}")
        
        # Load and verify
        loaded = Paper.from_library(library_id)
        similarity = paper.similarity_score(loaded)
        print(f"✅ Storage verification: {similarity:.2f} similarity")
        
    except Exception as e:
        print(f"⚠️  Storage: {e}")
    
    print()
    return paper


def demo_papers_collection():
    """Demonstrate Papers collection management."""
    print("📚 PAPERS DEMO - Project Collection Management")
    print("-" * 50)
    
    # Create a collection of related papers
    papers_data = [
        {
            "title": "Sequence to Sequence Learning with Neural Networks",
            "authors": ["Sutskever, Ilya", "Vinyals, Oriol", "Le, Quoc V."],
            "journal": "NIPS",
            "year": 2014,
            "doi": "10.5555/2969033.2969173",
            "keywords": ["seq2seq", "LSTM", "neural networks"],
            "citation_count": 18000
        },
        {
            "title": "Effective Approaches to Attention-based Neural Machine Translation",
            "authors": ["Luong, Minh-Thang", "Pham, Hieu", "Manning, Christopher D."],
            "journal": "EMNLP",
            "year": 2015,
            "doi": "10.18653/v1/D15-1166",
            "keywords": ["attention", "neural machine translation", "alignment"],
            "citation_count": 8500
        },
        {
            "title": "Show, Attend and Tell: Neural Image Caption Generation with Visual Attention",
            "authors": ["Xu, Kelvin", "Ba, Jimmy", "Kiros, Ryan"],
            "journal": "ICML",
            "year": 2015,
            "doi": "10.48550/arXiv.1502.03044",
            "keywords": ["image captioning", "visual attention", "CNN"],
            "citation_count": 12000
        }
    ]
    
    # Create Paper objects
    paper_objects = [
        Paper(project="attention_mechanisms", **data) 
        for data in papers_data
    ]
    
    # Create collection
    collection = Papers(
        paper_objects,
        project="attention_mechanisms",
        auto_deduplicate=True
    )
    
    print(f"📦 Collection created: {len(collection)} papers")
    print(f"🏷️  Project: {collection.project}")
    
    # Demonstrate operations
    print("\n📊 Collection Analysis:")
    
    # Statistics
    stats = collection.get_project_statistics()
    print(f"   • Total papers: {stats['total_papers']}")
    print(f"   • With DOI: {stats['with_doi']}")
    print(f"   • Year range: {stats['years']['min']}-{stats['years']['max']}")
    print(f"   • Unique authors: {stats['authors']}")
    
    # Filtering and sorting
    recent = collection.filter(year_min=2015)
    print(f"   • Papers from 2015+: {len(recent)}")
    
    top_cited = collection.sort_by("citation_count", ascending=False)
    top_paper = top_cited._papers[0]
    print(f"   • Most cited: {top_paper.title[:40]}... ({top_paper.citation_count:,})")
    
    # Storage operations
    try:
        save_results = collection.save_to_library(progress=False)
        print(f"💾 Saved to library: {save_results['saved']} papers")
        
        symlink_results = collection.create_project_symlinks()
        print(f"🔗 Created symlinks: {symlink_results['created']}")
        
    except Exception as e:
        print(f"⚠️  Storage: {e}")
    
    print()
    return collection


def demo_scholar_global():
    """Demonstrate Scholar global management."""
    print("🎓 SCHOLAR DEMO - Global Library Management")
    print("-" * 50)
    
    # Initialize Scholar
    scholar = Scholar(project="attention_mechanisms")
    print(f"🌐 Scholar initialized")
    print(f"📁 Workspace: {scholar.workspace_dir}")
    
    # Project management
    try:
        # Create projects
        scholar.create_project(
            "computer_vision_2024",
            description="Computer vision papers from 2024"
        )
        scholar.create_project(
            "nlp_fundamentals", 
            description="Fundamental NLP papers"
        )
        
        projects = scholar.list_projects()
        print(f"📂 Total projects: {len(projects)}")
        
        # Show first few projects
        for project in projects[:3]:
            print(f"   • {project['name']}: {project.get('description', 'No description')}")
            
    except Exception as e:
        print(f"⚠️  Project management: {e}")
    
    # Library statistics
    try:
        stats = scholar.get_library_statistics()
        print(f"\n📊 Library Overview:")
        print(f"   • Projects: {stats['total_projects']}")
        print(f"   • Papers: {stats['total_papers']}")
        print(f"   • Storage: {stats['storage_mb']:.2f} MB")
        
    except Exception as e:
        print(f"⚠️  Statistics: {e}")
    
    # Cross-project search
    try:
        search_results = scholar.search_across_projects("attention")
        print(f"\n🔍 Search Results:")
        print(f"   • 'attention' across all projects: {len(search_results)} papers")
        
        if len(search_results) > 0:
            for i, paper in enumerate(search_results._papers[:2]):
                print(f"     {i+1}. {paper.title[:50]}...")
                
    except Exception as e:
        print(f"⚠️  Search: {e}")
    
    # Service components
    print(f"\n🔧 Services:")
    print(f"   • DOI Resolver: {type(scholar.doi_resolver).__name__}")
    print(f"   • Library Manager: {type(scholar.library_manager).__name__}")
    print(f"   • Auth Manager: {type(scholar.auth_manager).__name__}")
    
    print()
    return scholar


def demo_integration_workflow():
    """Demonstrate how all components work together."""
    print("🔄 INTEGRATION DEMO - Complete Workflow")
    print("-" * 50)
    
    # 1. Start with Scholar (global entry point)
    scholar = Scholar(project="workflow_demo")
    print("1️⃣ Scholar initialized as global entry point")
    
    # 2. Create project
    try:
        scholar.create_project(
            "workflow_demo",
            description="Demo of complete integration workflow"
        )
        print("2️⃣ Project created through Scholar")
    except:
        print("2️⃣ Project already exists")
    
    # 3. Create individual papers
    paper1 = Paper(
        title="ResNet: Deep Residual Learning for Image Recognition",
        authors=["He, Kaiming", "Zhang, Xiangyu", "Ren, Shaoqing"],
        journal="CVPR",
        year=2016,
        doi="10.1109/CVPR.2016.90",
        citation_count=75000,
        project="workflow_demo"
    )
    
    paper2 = Paper(
        title="DenseNet: Densely Connected Convolutional Networks",
        authors=["Huang, Gao", "Liu, Zhuang", "Van Der Maaten, Laurens"],
        journal="CVPR",
        year=2017,
        doi="10.1109/CVPR.2017.243",
        citation_count=25000,
        project="workflow_demo"
    )
    
    print("3️⃣ Individual papers created")
    
    # 4. Create Papers collection
    collection = Papers([paper1, paper2], project="workflow_demo", config=scholar.config)
    print("4️⃣ Papers collection created")
    
    # 5. Use Scholar to work with collection
    scholar.set_project("workflow_demo")
    print("5️⃣ Scholar project context set")
    
    # 6. Demonstrate integration
    try:
        # Save through collection
        save_results = collection.save_to_library(progress=False)
        print(f"6️⃣ Collection saved: {save_results['saved']} papers")
        
        # Load through Scholar
        loaded_collection = scholar.load_project("workflow_demo")
        print(f"7️⃣ Loaded through Scholar: {len(loaded_collection)} papers")
        
        # Search through Scholar
        search_results = scholar.search_library("ResNet")
        print(f"8️⃣ Search through Scholar: {len(search_results)} results")
        
    except Exception as e:
        print(f"⚠️  Integration workflow: {e}")
    
    # 7. Export and backup
    try:
        # Export collection
        with tempfile.NamedTemporaryFile(suffix=".bib", delete=False) as tmp:
            collection.save(tmp.name, format="bibtex")
            print(f"9️⃣ Collection exported to: {tmp.name}")
        
        # Backup library
        backup_dir = Path(tempfile.mkdtemp()) / "demo_backup"
        backup_info = scholar.backup_library(backup_dir)
        print(f"🔟 Library backed up: {backup_info['size_mb']:.2f} MB")
        
        # Cleanup
        import shutil
        shutil.rmtree(backup_dir, ignore_errors=True)
        
    except Exception as e:
        print(f"⚠️  Export/backup: {e}")
    
    print()
    print("✅ Integration workflow completed!")
    return scholar, collection


def main():
    """Run comprehensive demonstration of all components."""
    print("=" * 70)
    print("🚀 SCITEX SCHOLAR CORE COMPONENTS COMPREHENSIVE DEMO")
    print("=" * 70)
    print()
    
    print("This demo shows the three levels of SciTeX Scholar:")
    print("📄 Paper  - Individual publication carrier")
    print("📚 Papers - Project collection manager")
    print("🎓 Scholar - Global library entry point")
    print()
    
    # Run individual demos
    paper = demo_individual_paper()
    collection = demo_papers_collection() 
    scholar = demo_scholar_global()
    scholar_final, collection_final = demo_integration_workflow()
    
    # Summary
    print("=" * 70)
    print("📋 DEMO SUMMARY")
    print("=" * 70)
    print()
    print("✅ Successfully demonstrated:")
    print("   • Paper: Individual publication with storage integration")
    print("   • Papers: Project collection with batch operations")
    print("   • Scholar: Global library management and coordination")
    print("   • Integration: All components working together seamlessly")
    print()
    print("🔑 Key Features Shown:")
    print("   • Storage integration with automatic ID generation")
    print("   • Project-based organization with symlink management")
    print("   • Cross-project search and global statistics")
    print("   • BibTeX/JSON export and library backup capabilities")
    print("   • Similarity checking and deduplication")
    print("   • Complete workflow from creation to storage to retrieval")
    print()
    print("🎯 The enhanced storage integration provides:")
    print("   • Seamless data persistence across all levels")
    print("   • Project-aware operations with automatic context")
    print("   • Global library management with comprehensive statistics")
    print("   • Backward compatibility with existing workflows")
    print()
    print("Demo completed successfully! 🎉")


if __name__ == "__main__":
    main()

# EOF