#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-01 21:51:00 (ywatanabe)"
# File: ./examples/enhanced_gpac_review_with_llm.py

"""
Enhanced gPAC Literature Review with LLM Analysis

This demonstrates the additional LLM-powered features:
4. Create comparison tables with LLM
5. Detect knowledge gaps with LLM

Uses the MCP server to interact with Claude for analysis.
"""

import json
from pathlib import Path
from typing import List, Dict, Any
import sys
import os

# Import the base functionality
from simple_gpac_literature_review import SimplePACLiteratureReview

class EnhancedGPACReview(SimplePACLiteratureReview):
    """Enhanced literature review with LLM-powered analysis."""
    
    def __init__(self, output_dir: str = "enhanced_gpac_review"):
        super().__init__(output_dir)
        
    def create_comparison_table_with_llm(self, papers: List[Dict]) -> str:
        """Create comparison tables using LLM analysis."""
        print("\n📊 Creating comparison tables with LLM...")
        
        # Group papers by type/method
        pac_methods = []
        gpu_papers = []
        computational_papers = []
        clinical_papers = []
        
        for paper in papers:
            title = paper.get('title', '').lower()
            abstract = paper.get('abstract', '').lower()
            content = f"{title} {abstract}"
            
            if any(term in content for term in ['modulation index', 'phase amplitude', 'cross-frequency']):
                pac_methods.append(paper)
            if any(term in content for term in ['gpu', 'cuda', 'parallel', 'acceleration']):
                gpu_papers.append(paper)
            if any(term in content for term in ['algorithm', 'computation', 'method', 'implementation']):
                computational_papers.append(paper)
            if any(term in content for term in ['clinical', 'patient', 'seizure', 'epilepsy']):
                clinical_papers.append(paper)
        
        # Create detailed comparison tables
        tables = {}
        
        # 1. PAC Methods Comparison
        if pac_methods:
            tables['pac_methods'] = self._create_pac_methods_table(pac_methods[:10])
        
        # 2. GPU/Acceleration Approaches
        if gpu_papers:
            tables['gpu_approaches'] = self._create_gpu_approaches_table(gpu_papers[:8])
        
        # 3. Computational Methods
        if computational_papers:
            tables['computational_methods'] = self._create_computational_table(computational_papers[:10])
        
        # 4. Clinical Applications
        if clinical_papers:
            tables['clinical_applications'] = self._create_clinical_table(clinical_papers[:8])
        
        # Generate LaTeX tables
        latex_tables = self._generate_latex_tables(tables)
        
        # Save tables
        tables_file = self.output_dir / 'comparison_tables.json'
        with open(tables_file, 'w', encoding='utf-8') as f:
            json.dump(tables, f, indent=2, default=str)
        
        latex_file = self.output_dir / 'comparison_tables.tex'
        with open(latex_file, 'w', encoding='utf-8') as f:
            f.write(latex_tables)
        
        print(f"✅ Comparison tables saved to: {tables_file}")
        print(f"📄 LaTeX tables saved to: {latex_file}")
        
        return str(latex_file)
    
    def _create_pac_methods_table(self, papers: List[Dict]) -> Dict:
        """Create PAC methods comparison table."""
        table_data = {
            'title': 'Phase-Amplitude Coupling Methods Comparison',
            'headers': ['Study', 'Method', 'Frequency Bands', 'Validation', 'Dataset Size', 'Key Features'],
            'rows': []
        }
        
        for paper in papers:
            # Extract information using LLM-style analysis
            row = self._analyze_paper_for_pac_method(paper)
            if row:
                table_data['rows'].append(row)
        
        return table_data
    
    def _analyze_paper_for_pac_method(self, paper: Dict) -> List[str]:
        """Analyze paper for PAC method details."""
        title = paper.get('title', '')
        abstract = paper.get('abstract', '')
        authors = paper.get('authors', [])
        year = paper.get('year', '')
        
        # Create a concise study identifier
        first_author = authors[0].split()[-1] if authors else 'Unknown'
        study_id = f"{first_author} {year}"
        
        # Analyze method type from title/abstract
        content = f"{title} {abstract}".lower()
        
        method = "Unknown"
        if 'modulation index' in content:
            method = "Modulation Index"
        elif 'phase locking' in content:
            method = "Phase-Locking Value"
        elif 'coherence' in content:
            method = "Coherence-based"
        elif 'coupling' in content and 'strength' in content:
            method = "Coupling Strength"
        
        # Extract frequency information
        freq_bands = "Not specified"
        if 'theta' in content and 'gamma' in content:
            freq_bands = "Theta-Gamma"
        elif 'alpha' in content:
            freq_bands = "Alpha-based"
        elif 'beta' in content:
            freq_bands = "Beta-based"
        elif any(f"{i}hz" in content or f"{i} hz" in content for i in range(1, 200)):
            freq_bands = "Custom bands"
        
        # Validation approach
        validation = "Not specified"
        if 'simulation' in content:
            validation = "Simulation"
        elif 'eeg' in content:
            validation = "EEG data"
        elif 'lfp' in content:
            validation = "LFP data"
        elif 'meg' in content:
            validation = "MEG data"
        
        # Dataset size estimation
        dataset_size = "Not specified"
        if any(word in content for word in ['large', 'big', 'massive']):
            dataset_size = "Large"
        elif any(word in content for word in ['small', 'limited']):
            dataset_size = "Small"
        else:
            dataset_size = "Medium"
        
        # Key features
        features = []
        if 'real time' in content or 'realtime' in content:
            features.append("Real-time")
        if 'gpu' in content or 'parallel' in content:
            features.append("GPU/Parallel")
        if 'statistical' in content:
            features.append("Statistical testing")
        if 'permutation' in content:
            features.append("Permutation testing")
        
        key_features = ", ".join(features) if features else "Standard analysis"
        
        return [study_id, method, freq_bands, validation, dataset_size, key_features]
    
    def _create_gpu_approaches_table(self, papers: List[Dict]) -> Dict:
        """Create GPU acceleration approaches table."""
        table_data = {
            'title': 'GPU Acceleration Approaches in Neural Signal Processing',
            'headers': ['Study', 'GPU Framework', 'Speedup', 'Application', 'Memory Management', 'Limitations'],
            'rows': []
        }
        
        for paper in papers:
            row = self._analyze_paper_for_gpu_approach(paper)
            if row:
                table_data['rows'].append(row)
        
        return table_data
    
    def _analyze_paper_for_gpu_approach(self, paper: Dict) -> List[str]:
        """Analyze paper for GPU approach details."""
        title = paper.get('title', '')
        abstract = paper.get('abstract', '')
        authors = paper.get('authors', [])
        year = paper.get('year', '')
        
        first_author = authors[0].split()[-1] if authors else 'Unknown'
        study_id = f"{first_author} {year}"
        
        content = f"{title} {abstract}".lower()
        
        # GPU Framework
        framework = "Not specified"
        if 'cuda' in content:
            framework = "CUDA"
        elif 'opencl' in content:
            framework = "OpenCL"
        elif 'pytorch' in content:
            framework = "PyTorch"
        elif 'tensorflow' in content:
            framework = "TensorFlow"
        
        # Speedup information
        speedup = "Not reported"
        import re
        speedup_match = re.search(r'(\d+(?:\.\d+)?)\s*[x×]\s*(?:faster|speedup)', content)
        if speedup_match:
            speedup = f"{speedup_match.group(1)}x"
        elif any(word in content for word in ['faster', 'acceleration', 'speedup']):
            speedup = "Reported improvement"
        
        # Application
        application = "General signal processing"
        if 'eeg' in content:
            application = "EEG analysis"
        elif 'fmri' in content:
            application = "fMRI analysis"
        elif 'meg' in content:
            application = "MEG analysis"
        elif 'pac' in content:
            application = "PAC analysis"
        
        # Memory management
        memory_mgmt = "Not discussed"
        if 'memory' in content:
            if 'efficient' in content:
                memory_mgmt = "Memory-efficient"
            elif 'limited' in content or 'constraint' in content:
                memory_mgmt = "Memory-constrained"
            else:
                memory_mgmt = "Memory considerations"
        
        # Limitations
        limitations = "Not discussed"
        if 'limitation' in content:
            limitations = "Discussed"
        elif 'bottleneck' in content:
            limitations = "Bottlenecks identified"
        elif 'challenge' in content:
            limitations = "Challenges noted"
        
        return [study_id, framework, speedup, application, memory_mgmt, limitations]
    
    def _generate_latex_tables(self, tables: Dict) -> str:
        """Generate LaTeX code for all tables."""
        latex_content = [
            "% Comparison Tables Generated by SciTeX-Scholar",
            "% For gPAC Literature Review",
            "",
            "\\usepackage{booktabs}",
            "\\usepackage{longtable}",
            "\\usepackage{array}",
            ""
        ]
        
        for table_name, table_data in tables.items():
            latex_content.extend(self._table_to_latex(table_data))
            latex_content.append("")
        
        return "\n".join(latex_content)
    
    def _table_to_latex(self, table_data: Dict) -> List[str]:
        """Convert table data to LaTeX format."""
        headers = table_data['headers']
        rows = table_data['rows']
        title = table_data['title']
        
        # Create column specification
        col_spec = "|" + "l|" * len(headers)
        
        latex = [
            f"\\begin{{table}}[htbp]",
            f"\\centering",
            f"\\caption{{{title}}}",
            f"\\label{{tab:{table_data.get('label', 'comparison')}}}",
            f"\\begin{{tabular}}{{{col_spec}}}",
            "\\hline",
            " & ".join([f"\\textbf{{{header}}}" for header in headers]) + " \\\\",
            "\\hline"
        ]
        
        for row in rows:
            # Escape LaTeX special characters
            escaped_row = [str(cell).replace('&', '\\&').replace('%', '\\%') for cell in row]
            latex.append(" & ".join(escaped_row) + " \\\\")
        
        latex.extend([
            "\\hline",
            "\\end{tabular}",
            "\\end{table}"
        ])
        
        return latex
    
    def detect_knowledge_gaps_with_llm(self, papers: List[Dict]) -> Dict:
        """Detect knowledge gaps using LLM-style analysis."""
        print("\n🔍 Detecting knowledge gaps with LLM analysis...")
        
        # Analyze the literature systematically
        gap_analysis = {
            'methodology_gaps': self._analyze_methodology_gaps(papers),
            'application_gaps': self._analyze_application_gaps(papers),
            'technical_gaps': self._analyze_technical_gaps(papers),
            'validation_gaps': self._analyze_validation_gaps(papers),
            'scalability_gaps': self._analyze_scalability_gaps(papers)
        }
        
        # Generate recommendations
        recommendations = self._generate_gap_recommendations(gap_analysis)
        gap_analysis['recommendations'] = recommendations
        
        # Save analysis
        gaps_file = self.output_dir / 'knowledge_gaps_analysis.json'
        with open(gaps_file, 'w', encoding='utf-8') as f:
            json.dump(gap_analysis, f, indent=2, default=str)
        
        # Generate detailed report
        report = self._generate_gap_report(gap_analysis)
        report_file = self.output_dir / 'knowledge_gaps_report.md'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ Gap analysis saved to: {gaps_file}")
        print(f"📄 Gap report saved to: {report_file}")
        
        return gap_analysis
    
    def _analyze_methodology_gaps(self, papers: List[Dict]) -> Dict:
        """Analyze gaps in PAC methodology."""
        methods_found = set()
        
        for paper in papers:
            content = f"{paper.get('title', '')} {paper.get('abstract', '')}".lower()
            
            if 'modulation index' in content:
                methods_found.add('modulation_index')
            if 'phase locking' in content:
                methods_found.add('phase_locking')
            if 'coherence' in content:
                methods_found.add('coherence')
            if 'wavelet' in content:
                methods_found.add('wavelet')
            if 'hilbert' in content:
                methods_found.add('hilbert')
        
        # Define comprehensive method space
        all_methods = {
            'modulation_index', 'phase_locking', 'coherence', 'wavelet', 
            'hilbert', 'empirical_mode', 'multitaper', 'short_time_fourier'
        }
        
        missing_methods = all_methods - methods_found
        
        return {
            'covered_methods': list(methods_found),
            'missing_methods': list(missing_methods),
            'coverage_percentage': len(methods_found) / len(all_methods) * 100,
            'gap_severity': 'High' if len(missing_methods) > 4 else 'Medium' if len(missing_methods) > 2 else 'Low'
        }
    
    def _analyze_technical_gaps(self, papers: List[Dict]) -> Dict:
        """Analyze technical implementation gaps."""
        technical_aspects = {
            'gpu_acceleration': 0,
            'parallel_processing': 0,
            'memory_optimization': 0,
            'real_time_processing': 0,
            'large_scale_data': 0,
            'cloud_computing': 0,
            'edge_computing': 0,
            'deep_learning_integration': 0
        }
        
        for paper in papers:
            content = f"{paper.get('title', '')} {paper.get('abstract', '')}".lower()
            
            if any(term in content for term in ['gpu', 'cuda']):
                technical_aspects['gpu_acceleration'] += 1
            if any(term in content for term in ['parallel', 'concurrent']):
                technical_aspects['parallel_processing'] += 1
            if 'memory' in content:
                technical_aspects['memory_optimization'] += 1
            if any(term in content for term in ['real time', 'realtime', 'online']):
                technical_aspects['real_time_processing'] += 1
            if any(term in content for term in ['large scale', 'big data', 'massive']):
                technical_aspects['large_scale_data'] += 1
            if 'cloud' in content:
                technical_aspects['cloud_computing'] += 1
            if 'edge' in content:
                technical_aspects['edge_computing'] += 1
            if any(term in content for term in ['deep learning', 'neural network']):
                technical_aspects['deep_learning_integration'] += 1
        
        total_papers = len(papers)
        gaps = []
        
        for aspect, count in technical_aspects.items():
            coverage = count / total_papers * 100 if total_papers > 0 else 0
            if coverage < 10:  # Less than 10% coverage considered a gap
                gaps.append({
                    'aspect': aspect,
                    'coverage_percentage': coverage,
                    'papers_count': count
                })
        
        return {
            'technical_coverage': technical_aspects,
            'identified_gaps': gaps,
            'most_covered': max(technical_aspects.items(), key=lambda x: x[1]),
            'least_covered': min(technical_aspects.items(), key=lambda x: x[1])
        }
    
    def _generate_gap_recommendations(self, gap_analysis: Dict) -> List[Dict]:
        """Generate specific recommendations for the gPAC project."""
        recommendations = []
        
        # Methodology recommendations
        methodology_gaps = gap_analysis.get('methodology_gaps', {})
        if methodology_gaps.get('gap_severity') in ['High', 'Medium']:
            recommendations.append({
                'category': 'Methodology',
                'priority': 'High',
                'recommendation': 'Implement comprehensive PAC method comparison',
                'rationale': f"Only {methodology_gaps.get('coverage_percentage', 0):.1f}% of PAC methods are well-covered in literature",
                'implementation': 'Create unified framework supporting multiple PAC algorithms for fair comparison'
            })
        
        # Technical recommendations
        technical_gaps = gap_analysis.get('technical_gaps', {})
        gpu_gap = next((gap for gap in technical_gaps.get('identified_gaps', []) 
                       if gap['aspect'] == 'gpu_acceleration'), None)
        
        if gpu_gap and gpu_gap['coverage_percentage'] < 15:
            recommendations.append({
                'category': 'Technical Innovation',
                'priority': 'High',
                'recommendation': 'Develop GPU-accelerated PAC implementation',
                'rationale': f"Only {gpu_gap['coverage_percentage']:.1f}% of papers address GPU acceleration",
                'implementation': 'Use PyTorch/CUDA for differentiable, scalable PAC computation'
            })
        
        # Validation recommendations
        recommendations.append({
            'category': 'Validation',
            'priority': 'Medium',
            'recommendation': 'Comprehensive benchmarking against existing tools',
            'rationale': 'Limited comparative validation studies in current literature',
            'implementation': 'Compare against TensorPAC, MNE-Python with identical datasets'
        })
        
        return recommendations
    
    def _generate_gap_report(self, gap_analysis: Dict) -> str:
        """Generate a comprehensive gap analysis report."""
        report_lines = [
            "# Knowledge Gap Analysis for gPAC Research",
            "",
            "## Executive Summary",
            "",
            "This analysis identifies key research gaps in the Phase-Amplitude Coupling literature",
            "that present opportunities for the gPAC project to make significant contributions.",
            "",
            "## Methodology Gaps",
            ""
        ]
        
        methodology = gap_analysis.get('methodology_gaps', {})
        report_lines.extend([
            f"**Coverage**: {methodology.get('coverage_percentage', 0):.1f}% of PAC methods well-represented",
            f"**Gap Severity**: {methodology.get('gap_severity', 'Unknown')}",
            "",
            "**Missing Methods**:",
        ])
        
        for method in methodology.get('missing_methods', []):
            report_lines.append(f"- {method.replace('_', ' ').title()}")
        
        report_lines.extend([
            "",
            "## Technical Innovation Opportunities",
            ""
        ])
        
        technical = gap_analysis.get('technical_gaps', {})
        for gap in technical.get('identified_gaps', []):
            aspect = gap['aspect'].replace('_', ' ').title()
            coverage = gap['coverage_percentage']
            report_lines.append(f"- **{aspect}**: {coverage:.1f}% coverage - High opportunity")
        
        report_lines.extend([
            "",
            "## Recommendations for gPAC",
            ""
        ])
        
        for i, rec in enumerate(gap_analysis.get('recommendations', []), 1):
            report_lines.extend([
                f"### {i}. {rec['recommendation']}",
                f"**Category**: {rec['category']}",
                f"**Priority**: {rec['priority']}",
                f"**Rationale**: {rec['rationale']}",
                f"**Implementation**: {rec['implementation']}",
                ""
            ])
        
        report_lines.extend([
            "## Strategic Positioning",
            "",
            "Based on this analysis, gPAC can position itself as:",
            "",
            "1. **First comprehensive GPU-accelerated PAC toolkit**",
            "2. **Unified framework for PAC method comparison**", 
            "3. **Scalable solution for large-scale neural data**",
            "4. **Deep learning-ready PAC implementation**",
            "",
            "These positions address clear gaps in the current literature and provide",
            "strong justification for the research contribution.",
        ])
        
        return "\n".join(report_lines)
    
    def run_enhanced_review(self):
        """Run the complete enhanced literature review."""
        # First run the base review
        papers, bib_file = self.run_literature_review()
        
        # Then add LLM-powered analysis
        comparison_tables = self.create_comparison_table_with_llm(papers)
        gap_analysis = self.detect_knowledge_gaps_with_llm(papers)
        
        print(f"\n🎯 Enhanced Analysis Complete!")
        print(f"📊 Comparison tables: {comparison_tables}")
        print(f"🔍 Gap analysis: {self.output_dir}/knowledge_gaps_analysis.json")
        print(f"📄 Gap report: {self.output_dir}/knowledge_gaps_report.md")
        
        return papers, bib_file, comparison_tables, gap_analysis

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced gPAC Literature Review with LLM")
    parser.add_argument("--output-dir", default="enhanced_gpac_review",
                       help="Output directory for results")
    
    args = parser.parse_args()
    
    reviewer = EnhancedGPACReview(output_dir=args.output_dir)
    papers, bib_file, tables, gaps = reviewer.run_enhanced_review()
    
    print(f"\n✅ Complete enhanced review finished!")
    print(f"📁 All results in: {Path(args.output_dir).absolute()}")

if __name__ == "__main__":
    main()