#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-12 03:55:00"
# Author: Claude
# Description: Example with visualizations using mngs

"""
SciTeX-Scholar Examples with Visualizations

This example demonstrates the system capabilities with visual outputs
including animated GIFs showing the search and analysis process.
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import json
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Try to import mngs for advanced visualizations
try:
    import mngs
    MNGS_AVAILABLE = True
except ImportError:
    MNGS_AVAILABLE = False
    print("Note: mngs not available. Using matplotlib directly.")

# Import our modules
try:
    from scitex_scholar.text_processor import TextProcessor
    from scitex_scholar.search_engine import SearchEngine
    from scitex_scholar.latex_parser import LaTeXParser
except ImportError:
    print("Note: SciTeX-Scholar modules not in path. Demonstrating visualization concepts.")


class VisualizationDemo:
    """Demo class for creating visualizations of the search process."""
    
    def __init__(self, output_dir="./demo_visualizations"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Configure matplotlib
        plt.style.use('seaborn-v0_8-darkgrid')
        if MNGS_AVAILABLE:
            # Use mngs configuration if available
            try:
                mngs.plt._configure_mpl()
            except:
                pass
    
    def create_search_process_animation(self):
        """Create an animated GIF showing the search process."""
        print("\n=== Creating Search Process Animation ===")
        
        # Simulate search process steps
        steps = [
            "1. Query Input: 'deep learning medical imaging'",
            "2. Query Expansion: +neural +networks +CNN +medical",
            "3. Vector Embedding: Converting to 768-dim vector",
            "4. Similarity Search: Finding nearest neighbors",
            "5. Ranking Results: Scoring by relevance",
            "6. Returning Top Results"
        ]
        
        # Create frames for animation
        fig, ax = plt.subplots(figsize=(10, 6))
        frames = []
        
        for i, step in enumerate(steps):
            ax.clear()
            ax.text(0.5, 0.7, "SciTeX-Scholar Process", 
                   ha='center', va='center', fontsize=20, fontweight='bold')
            
            # Show all previous steps in gray
            for j in range(i+1):
                color = 'green' if j == i else 'gray'
                alpha = 1.0 if j == i else 0.5
                ax.text(0.1, 0.5 - j*0.1, steps[j], 
                       fontsize=12, color=color, alpha=alpha)
            
            # Add progress bar
            progress = (i + 1) / len(steps)
            ax.barh(0.05, progress, height=0.05, 
                   color='green', alpha=0.7)
            ax.text(0.5, 0.02, f"Progress: {progress*100:.0f}%", 
                   ha='center', fontsize=10)
            
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            # Save frame
            frame_path = self.output_dir / f"search_frame_{i:02d}.png"
            plt.savefig(frame_path, bbox_inches='tight', dpi=100)
            frames.append(frame_path)
        
        plt.close()
        
        # Create GIF using imageio if available
        try:
            import imageio
            images = [imageio.imread(str(f)) for f in frames]
            gif_path = self.output_dir / "search_process.gif"
            imageio.mimsave(str(gif_path), images, duration=1.0)
            print(f"✓ Created animation: {gif_path}")
            
            # Clean up frames
            for f in frames:
                f.unlink()
        except ImportError:
            print("Note: imageio not installed. Frames saved as PNGs.")
        
        return frames
    
    def visualize_vector_embeddings(self):
        """Visualize vector embeddings in 2D space."""
        print("\n=== Creating Vector Embedding Visualization ===")
        
        # Simulate embeddings (in reality, these would be from SciBERT)
        np.random.seed(42)
        n_papers = 50
        
        # Create clusters
        clusters = {
            'Deep Learning': np.random.randn(15, 2) + [2, 2],
            'Medical Imaging': np.random.randn(15, 2) + [-2, 2],
            'NLP': np.random.randn(10, 2) + [2, -2],
            'Traditional ML': np.random.randn(10, 2) + [-2, -2]
        }
        
        # Create visualization
        fig, ax = plt.subplots(figsize=(10, 8))
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        for (label, points), color in zip(clusters.items(), colors):
            ax.scatter(points[:, 0], points[:, 1], 
                      label=label, alpha=0.6, s=100, color=color)
        
        # Add query point
        query_point = np.array([0, 0])
        ax.scatter(query_point[0], query_point[1], 
                  color='red', s=200, marker='*', 
                  label='Query', edgecolor='black', linewidth=2)
        
        # Draw arrows to nearest neighbors
        for label, points in clusters.items():
            distances = np.linalg.norm(points - query_point, axis=1)
            nearest_idx = np.argmin(distances)
            nearest = points[nearest_idx]
            
            ax.annotate('', xy=nearest, xytext=query_point,
                       arrowprops=dict(arrowstyle='->', 
                                     color='red', alpha=0.3, lw=2))
        
        ax.set_xlabel('Dimension 1 (reduced from 768D)', fontsize=12)
        ax.set_ylabel('Dimension 2 (reduced from 768D)', fontsize=12)
        ax.set_title('Vector Embeddings of Scientific Papers\n(2D projection using t-SNE)', 
                    fontsize=16, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Add explanation
        ax.text(0.02, 0.02, 
               'Red star: Query embedding\nArrows: Semantic similarity connections',
               transform=ax.transAxes, fontsize=10,
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        embed_path = self.output_dir / "vector_embeddings.png"
        plt.savefig(embed_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Created visualization: {embed_path}")
    
    def create_literature_analysis_charts(self):
        """Create charts showing literature analysis results."""
        print("\n=== Creating Literature Analysis Charts ===")
        
        # Simulate analysis data
        methods = ['CNN', 'RNN', 'Transformer', 'SVM', 'Random Forest', 
                  'LSTM', 'GAN', 'ResNet', 'BERT', 'U-Net']
        counts = [45, 23, 38, 15, 12, 28, 19, 34, 31, 29]
        
        years = list(range(2018, 2025))
        papers_per_year = [12, 18, 25, 32, 45, 58, 42]
        
        # Create subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Methods frequency
        ax1.barh(methods, counts, color='skyblue', edgecolor='navy')
        ax1.set_xlabel('Number of Papers', fontsize=12)
        ax1.set_title('Most Common Methods in Literature', fontsize=14, fontweight='bold')
        ax1.grid(axis='x', alpha=0.3)
        
        # 2. Publication timeline
        ax2.plot(years, papers_per_year, marker='o', linewidth=2, 
                markersize=8, color='green')
        ax2.fill_between(years, papers_per_year, alpha=0.3, color='green')
        ax2.set_xlabel('Year', fontsize=12)
        ax2.set_ylabel('Number of Papers', fontsize=12)
        ax2.set_title('Publication Trend Over Time', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        # 3. Research areas pie chart
        areas = ['Computer Vision', 'NLP', 'Medical AI', 'Robotics', 'Other']
        sizes = [35, 25, 20, 10, 10]
        colors_pie = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc']
        
        ax3.pie(sizes, labels=areas, colors=colors_pie, autopct='%1.1f%%',
                startangle=90, shadow=True)
        ax3.set_title('Research Areas Distribution', fontsize=14, fontweight='bold')
        
        # 4. Citation network simulation
        ax4.set_title('Citation Network Visualization', fontsize=14, fontweight='bold')
        
        # Create random network
        n_nodes = 20
        pos = np.random.rand(n_nodes, 2)
        
        # Draw nodes
        node_sizes = np.random.randint(100, 500, n_nodes)
        ax4.scatter(pos[:, 0], pos[:, 1], s=node_sizes, 
                   alpha=0.6, c=node_sizes, cmap='viridis')
        
        # Draw edges (citations)
        n_edges = 30
        for _ in range(n_edges):
            i, j = np.random.choice(n_nodes, 2, replace=False)
            ax4.plot([pos[i, 0], pos[j, 0]], 
                    [pos[i, 1], pos[j, 1]], 
                    'k-', alpha=0.2)
        
        ax4.set_xlim(-0.1, 1.1)
        ax4.set_ylim(-0.1, 1.1)
        ax4.axis('off')
        ax4.text(0.5, -0.05, 'Node size = citation count', 
                ha='center', transform=ax4.transAxes, fontsize=10)
        
        plt.suptitle('SciTeX-Scholar Literature Analysis Dashboard', 
                    fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        analysis_path = self.output_dir / "literature_analysis.png"
        plt.savefig(analysis_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Created visualization: {analysis_path}")
    
    def create_search_results_animation(self):
        """Create animated visualization of search results ranking."""
        print("\n=== Creating Search Results Animation ===")
        
        # Sample papers with scores
        papers = [
            ("Deep Learning for Medical Image Segmentation", 0.95),
            ("CNN-based Tumor Detection in MRI Scans", 0.92),
            ("Transformer Models for Medical Diagnosis", 0.88),
            ("Traditional ML in Healthcare", 0.75),
            ("Survey of AI in Medicine", 0.70),
        ]
        
        frames = []
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Animate the ranking process
        for step in range(len(papers) + 1):
            ax.clear()
            ax.set_title('Search Results Ranking Process', 
                        fontsize=16, fontweight='bold')
            
            # Show papers revealed so far
            for i in range(min(step, len(papers))):
                title, score = papers[i]
                y_pos = 0.8 - i * 0.15
                
                # Draw result box
                rect = plt.Rectangle((0.1, y_pos - 0.05), 0.8, 0.1, 
                                   facecolor='lightblue', 
                                   edgecolor='darkblue', 
                                   alpha=0.7)
                ax.add_patch(rect)
                
                # Add text
                ax.text(0.15, y_pos, f"{i+1}. {title[:40]}...", 
                       fontsize=11, va='center')
                ax.text(0.85, y_pos, f"{score:.2f}", 
                       fontsize=11, va='center', ha='right', 
                       fontweight='bold', color='darkgreen')
            
            # Add loading indicator for next paper
            if step < len(papers):
                ax.text(0.5, 0.8 - step * 0.15, "Calculating relevance...", 
                       ha='center', va='center', style='italic', 
                       color='gray')
            
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            # Add score legend
            ax.text(0.85, 0.95, "Score", fontsize=10, 
                   ha='right', fontweight='bold')
            
            # Save frame
            frame_path = self.output_dir / f"results_frame_{step:02d}.png"
            plt.savefig(frame_path, bbox_inches='tight', dpi=100)
            frames.append(frame_path)
        
        plt.close()
        
        # Create GIF
        try:
            import imageio
            images = [imageio.imread(str(f)) for f in frames]
            gif_path = self.output_dir / "search_results.gif"
            imageio.mimsave(str(gif_path), images, duration=0.8)
            print(f"✓ Created animation: {gif_path}")
            
            # Clean up frames
            for f in frames:
                f.unlink()
        except ImportError:
            print("Note: imageio not installed. Frames saved as PNGs.")
    
    def create_processing_pipeline_diagram(self):
        """Create a diagram showing the processing pipeline."""
        print("\n=== Creating Processing Pipeline Diagram ===")
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Pipeline stages
        stages = [
            ("PDF Input", 0.1, 0.8),
            ("Text Extraction", 0.3, 0.8),
            ("LaTeX Parsing", 0.5, 0.8),
            ("Entity Extraction", 0.7, 0.8),
            ("Vector Embedding", 0.9, 0.8),
            ("Index Storage", 0.5, 0.5),
            ("Search Query", 0.1, 0.2),
            ("Query Embedding", 0.3, 0.2),
            ("Similarity Search", 0.5, 0.2),
            ("Result Ranking", 0.7, 0.2),
            ("Output", 0.9, 0.2),
        ]
        
        # Draw boxes
        for i, (label, x, y) in enumerate(stages):
            if i < 5:  # Processing flow
                color = 'lightblue'
            elif i == 5:  # Storage
                color = 'lightgreen'
            else:  # Search flow
                color = 'lightyellow'
            
            rect = plt.Rectangle((x-0.08, y-0.05), 0.16, 0.1,
                               facecolor=color, edgecolor='black', lw=2)
            ax.add_patch(rect)
            ax.text(x, y, label, ha='center', va='center', fontsize=10,
                   fontweight='bold')
        
        # Draw arrows
        arrows = [
            (0, 1), (1, 2), (2, 3), (3, 4), (4, 5),  # Processing flow
            (6, 7), (7, 8), (8, 9), (9, 10),  # Search flow
            (5, 8),  # Storage to search connection
        ]
        
        for start_idx, end_idx in arrows:
            start = stages[start_idx]
            end = stages[end_idx]
            ax.annotate('', xy=(end[1], end[2]), 
                       xytext=(start[1], start[2]),
                       arrowprops=dict(arrowstyle='->', lw=2, color='darkblue'))
        
        # Add labels
        ax.text(0.5, 0.95, 'SciTeX-Scholar Processing Pipeline', 
               ha='center', fontsize=18, fontweight='bold')
        ax.text(0.5, 0.65, 'Document Processing', 
               ha='center', fontsize=12, style='italic', color='blue')
        ax.text(0.5, 0.35, 'Search & Retrieval', 
               ha='center', fontsize=12, style='italic', color='orange')
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        pipeline_path = self.output_dir / "processing_pipeline.png"
        plt.savefig(pipeline_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Created visualization: {pipeline_path}")


def main():
    """Run all visualization demos."""
    print("SciTeX-Scholar Visualization Examples")
    print("=" * 50)
    
    demo = VisualizationDemo()
    
    # Create all visualizations
    demo.create_search_process_animation()
    demo.visualize_vector_embeddings()
    demo.create_literature_analysis_charts()
    demo.create_search_results_animation()
    demo.create_processing_pipeline_diagram()
    
    print("\n" + "=" * 50)
    print("✓ All visualizations created!")
    print(f"✓ Check the output directory: {demo.output_dir}")
    
    # Create index.html to view all outputs
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SciTeX-Scholar Visualizations</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1 { color: #333; }
            .viz-container { margin: 20px 0; }
            img { max-width: 100%; height: auto; border: 1px solid #ddd; }
            .description { color: #666; margin: 10px 0; }
        </style>
    </head>
    <body>
        <h1>SciTeX-Scholar Visualization Gallery</h1>
        
        <div class="viz-container">
            <h2>1. Search Process Animation</h2>
            <p class="description">Shows the step-by-step process of semantic search.</p>
            <img src="search_process.gif" alt="Search Process">
        </div>
        
        <div class="viz-container">
            <h2>2. Vector Embeddings Visualization</h2>
            <p class="description">2D projection of paper embeddings showing semantic clusters.</p>
            <img src="vector_embeddings.png" alt="Vector Embeddings">
        </div>
        
        <div class="viz-container">
            <h2>3. Literature Analysis Dashboard</h2>
            <p class="description">Statistical analysis of the literature corpus.</p>
            <img src="literature_analysis.png" alt="Literature Analysis">
        </div>
        
        <div class="viz-container">
            <h2>4. Search Results Ranking</h2>
            <p class="description">Animation showing how results are ranked by relevance.</p>
            <img src="search_results.gif" alt="Search Results">
        </div>
        
        <div class="viz-container">
            <h2>5. Processing Pipeline</h2>
            <p class="description">Complete document processing and search pipeline.</p>
            <img src="processing_pipeline.png" alt="Processing Pipeline">
        </div>
    </body>
    </html>
    """
    
    index_path = demo.output_dir / "index.html"
    with open(index_path, 'w') as f:
        f.write(html_content)
    
    print(f"✓ Created HTML gallery: {index_path}")
    print("\nTo view: Open index.html in your browser")


if __name__ == "__main__":
    main()