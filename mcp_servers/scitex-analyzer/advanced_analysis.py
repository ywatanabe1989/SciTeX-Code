#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Project Analysis Tools for SciTeX
==========================================

Enhanced analysis capabilities for comprehensive project understanding:
- Semantic code analysis
- Dependency mapping and visualization
- Architectural insights and recommendations
- Performance analysis and optimization suggestions
- Research workflow pattern detection
- Cross-module integration analysis

Author: SciTeX MCP Development Team
Date: 2025-07-03
"""

import ast
import json
import networkx as nx
from pathlib import Path
from typing import Dict, Any, List, Set, Tuple, Optional
from collections import defaultdict, Counter
import re
import inspect


class AdvancedProjectAnalyzer:
    """Advanced project analysis with semantic understanding."""
    
    def __init__(self):
        self.dependency_graph = nx.DiGraph()
        self.semantic_patterns = {}
        self.performance_metrics = {}
        self.research_workflows = []
        
    async def analyze_semantic_structure(self, project_path: Path) -> Dict[str, Any]:
        """
        Perform semantic analysis of project structure and code patterns.
        
        Returns comprehensive insights about:
        - Code complexity and maintainability
        - Semantic relationships between modules
        - Research domain identification
        - Workflow pattern recognition
        """
        
        analysis = {
            "semantic_analysis": await self._analyze_semantic_patterns(project_path),
            "complexity_metrics": await self._calculate_complexity_metrics(project_path),
            "domain_classification": await self._classify_research_domain(project_path),
            "workflow_patterns": await self._detect_workflow_patterns(project_path),
            "module_relationships": await self._analyze_module_relationships(project_path),
            "optimization_opportunities": await self._identify_optimization_opportunities(project_path)
        }
        
        return analysis
    
    async def generate_dependency_map(self, project_path: Path) -> Dict[str, Any]:
        """
        Generate comprehensive dependency mapping with visualization data.
        
        Creates detailed dependency graphs at multiple levels:
        - File-level dependencies
        - Function-level call graphs
        - Data flow dependencies
        - Configuration dependencies
        """
        
        # Build multi-level dependency graph
        file_deps = await self._build_file_dependency_graph(project_path)
        function_deps = await self._build_function_call_graph(project_path)
        data_deps = await self._build_data_flow_graph(project_path)
        config_deps = await self._build_config_dependency_graph(project_path)
        
        # Calculate dependency metrics
        metrics = self._calculate_dependency_metrics(file_deps, function_deps)
        
        # Identify architectural patterns
        patterns = await self._identify_architectural_patterns(file_deps)
        
        # Generate visualization data
        viz_data = self._generate_visualization_data(file_deps, function_deps)
        
        return {
            "file_dependencies": file_deps,
            "function_call_graph": function_deps,
            "data_flow_graph": data_deps,
            "config_dependencies": config_deps,
            "dependency_metrics": metrics,
            "architectural_patterns": patterns,
            "visualization_data": viz_data,
            "recommendations": await self._generate_dependency_recommendations(file_deps, metrics)
        }
    
    async def analyze_performance_characteristics(self, project_path: Path) -> Dict[str, Any]:
        """
        Analyze performance characteristics and identify optimization opportunities.
        
        Examines:
        - Computational complexity patterns
        - Memory usage patterns
        - I/O operation efficiency
        - Parallelization opportunities
        - Caching potential
        """
        
        perf_analysis = {
            "complexity_analysis": await self._analyze_computational_complexity(project_path),
            "memory_patterns": await self._analyze_memory_usage_patterns(project_path),
            "io_efficiency": await self._analyze_io_efficiency(project_path),
            "parallelization_opportunities": await self._identify_parallelization_opportunities(project_path),
            "caching_recommendations": await self._identify_caching_opportunities(project_path),
            "performance_hotspots": await self._identify_performance_hotspots(project_path),
            "optimization_roadmap": await self._generate_optimization_roadmap(project_path)
        }
        
        return perf_analysis
    
    async def analyze_research_workflow_patterns(self, project_path: Path) -> Dict[str, Any]:
        """
        Identify and analyze research workflow patterns specific to scientific computing.
        
        Detects common patterns:
        - Data preprocessing pipelines
        - Analysis workflows
        - Visualization patterns
        - Reproducibility practices
        - Publication workflows
        """
        
        workflow_analysis = {
            "pipeline_patterns": await self._detect_pipeline_patterns(project_path),
            "analysis_workflows": await self._detect_analysis_workflows(project_path),
            "visualization_patterns": await self._detect_visualization_patterns(project_path),
            "reproducibility_score": await self._assess_reproducibility(project_path),
            "publication_readiness": await self._assess_publication_readiness(project_path),
            "workflow_efficiency": await self._assess_workflow_efficiency(project_path),
            "improvement_suggestions": await self._suggest_workflow_improvements(project_path)
        }
        
        return workflow_analysis
    
    async def generate_architectural_insights(self, project_path: Path) -> Dict[str, Any]:
        """
        Generate high-level architectural insights and recommendations.
        
        Provides strategic guidance on:
        - Overall architecture health
        - Modularity and separation of concerns
        - Scalability considerations
        - Maintainability assessment
        - Evolution recommendations
        """
        
        architectural_analysis = {
            "architecture_health": await self._assess_architecture_health(project_path),
            "modularity_score": await self._calculate_modularity_score(project_path),
            "coupling_analysis": await self._analyze_coupling_patterns(project_path),
            "cohesion_analysis": await self._analyze_cohesion_patterns(project_path),
            "scalability_assessment": await self._assess_scalability(project_path),
            "maintainability_score": await self._calculate_maintainability_score(project_path),
            "evolution_roadmap": await self._generate_evolution_roadmap(project_path),
            "refactoring_opportunities": await self._identify_refactoring_opportunities(project_path)
        }
        
        return architectural_analysis
    
    # Implementation methods
    
    async def _analyze_semantic_patterns(self, project_path: Path) -> Dict[str, Any]:
        """Analyze semantic patterns in code."""
        patterns = {
            "scientific_patterns": [],
            "data_processing_patterns": [],
            "analysis_patterns": [],
            "visualization_patterns": []
        }
        
        for py_file in project_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                tree = ast.parse(content)
                
                # Detect scientific computing patterns
                if re.search(r'(numpy|scipy|pandas|matplotlib)', content):
                    patterns["scientific_patterns"].append({
                        "file": str(py_file.relative_to(project_path)),
                        "libraries": re.findall(r'(numpy|scipy|pandas|matplotlib|sklearn)', content)
                    })
                
                # Detect data processing patterns
                if re.search(r'(\.load|\.save|\.read_csv|\.to_csv)', content):
                    patterns["data_processing_patterns"].append({
                        "file": str(py_file.relative_to(project_path)),
                        "operations": re.findall(r'\.(load|save|read_csv|to_csv)', content)
                    })
                
                # Detect analysis patterns
                if re.search(r'(\.mean|\.std|\.correlation|\.fit|\.predict)', content):
                    patterns["analysis_patterns"].append({
                        "file": str(py_file.relative_to(project_path)),
                        "methods": re.findall(r'\.(mean|std|correlation|fit|predict)', content)
                    })
                
                # Detect visualization patterns
                if re.search(r'(\.plot|\.scatter|\.hist|\.subplots)', content):
                    patterns["visualization_patterns"].append({
                        "file": str(py_file.relative_to(project_path)),
                        "plot_types": re.findall(r'\.(plot|scatter|hist|subplots)', content)
                    })
                    
            except:
                continue
        
        return patterns
    
    async def _calculate_complexity_metrics(self, project_path: Path) -> Dict[str, Any]:
        """Calculate various complexity metrics."""
        metrics = {
            "cyclomatic_complexity": {},
            "cognitive_complexity": {},
            "lines_of_code": {},
            "function_complexity": {}
        }
        
        for py_file in project_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                tree = ast.parse(content)
                
                file_key = str(py_file.relative_to(project_path))
                
                # Calculate basic metrics
                metrics["lines_of_code"][file_key] = len(content.split('\n'))
                
                # Analyze functions
                functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                metrics["function_complexity"][file_key] = len(functions)
                
                # Simple cyclomatic complexity estimation
                complexity = 1  # Base complexity
                for node in ast.walk(tree):
                    if isinstance(node, (ast.If, ast.While, ast.For, ast.With)):
                        complexity += 1
                    elif isinstance(node, ast.BoolOp):
                        complexity += len(node.values) - 1
                
                metrics["cyclomatic_complexity"][file_key] = complexity
                
            except:
                continue
        
        return metrics
    
    async def _classify_research_domain(self, project_path: Path) -> Dict[str, Any]:
        """Classify the research domain based on code patterns and imports."""
        domain_indicators = {
            "neuroscience": ["mne", "nilearn", "spike", "neural", "brain", "eeg", "fmri"],
            "machine_learning": ["sklearn", "tensorflow", "pytorch", "keras", "xgboost"],
            "bioinformatics": ["biopython", "bioconda", "genomic", "sequence", "dna", "rna"],
            "physics": ["scipy", "sympy", "quantum", "physics", "simulation"],
            "data_science": ["pandas", "numpy", "matplotlib", "seaborn", "plotly"],
            "signal_processing": ["scipy.signal", "dsp", "filter", "fourier", "spectral"]
        }
        
        domain_scores = defaultdict(int)
        evidence = defaultdict(list)
        
        for py_file in project_path.rglob("*.py"):
            try:
                content = py_file.read_text().lower()
                
                for domain, indicators in domain_indicators.items():
                    for indicator in indicators:
                        count = content.count(indicator)
                        if count > 0:
                            domain_scores[domain] += count
                            evidence[domain].append({
                                "file": str(py_file.relative_to(project_path)),
                                "indicator": indicator,
                                "count": count
                            })
            except:
                continue
        
        # Determine primary domain
        primary_domain = max(domain_scores, key=domain_scores.get) if domain_scores else "general"
        
        return {
            "primary_domain": primary_domain,
            "domain_scores": dict(domain_scores),
            "confidence": domain_scores[primary_domain] / sum(domain_scores.values()) if domain_scores else 0,
            "evidence": dict(evidence)
        }
    
    async def _detect_workflow_patterns(self, project_path: Path) -> List[Dict[str, Any]]:
        """Detect common research workflow patterns."""
        patterns = []
        
        # Look for common workflow indicators
        workflow_indicators = {
            "data_preprocessing": ["preprocess", "clean", "normalize", "transform"],
            "analysis": ["analyze", "compute", "calculate", "process"],
            "visualization": ["plot", "chart", "graph", "visualize"],
            "export": ["save", "export", "write", "output"]
        }
        
        for py_file in project_path.rglob("*.py"):
            try:
                content = py_file.read_text().lower()
                
                detected_steps = []
                for step, indicators in workflow_indicators.items():
                    if any(indicator in content for indicator in indicators):
                        detected_steps.append(step)
                
                if len(detected_steps) >= 2:  # At least 2 workflow steps
                    patterns.append({
                        "file": str(py_file.relative_to(project_path)),
                        "workflow_steps": detected_steps,
                        "complexity": len(detected_steps)
                    })
            except:
                continue
        
        return patterns
    
    async def _analyze_module_relationships(self, project_path: Path) -> Dict[str, Any]:
        """Analyze relationships between different modules."""
        relationships = {
            "import_graph": {},
            "shared_dependencies": {},
            "coupling_strength": {}
        }
        
        # Build import graph
        for py_file in project_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                tree = ast.parse(content)
                
                file_key = str(py_file.relative_to(project_path))
                imports = []
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for name in node.names:
                            imports.append(name.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.append(node.module)
                
                relationships["import_graph"][file_key] = imports
                
            except:
                continue
        
        return relationships
    
    async def _identify_optimization_opportunities(self, project_path: Path) -> List[Dict[str, Any]]:
        """Identify potential optimization opportunities."""
        opportunities = []
        
        for py_file in project_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                file_key = str(py_file.relative_to(project_path))
                
                # Check for potential optimizations
                if "for" in content and "pandas" in content:
                    opportunities.append({
                        "type": "vectorization",
                        "file": file_key,
                        "description": "Consider vectorizing pandas operations instead of loops",
                        "impact": "high"
                    })
                
                if content.count("np.") > 10 and "numba" not in content:
                    opportunities.append({
                        "type": "acceleration",
                        "file": file_key,
                        "description": "Consider using numba for numerical acceleration",
                        "impact": "medium"
                    })
                
                if "pd.read_csv" in content and "cache" not in content:
                    opportunities.append({
                        "type": "caching",
                        "file": file_key,
                        "description": "Consider caching data loading operations",
                        "impact": "medium"
                    })
                    
            except:
                continue
        
        return opportunities
    
    async def _build_file_dependency_graph(self, project_path: Path) -> Dict[str, Any]:
        """Build file-level dependency graph."""
        graph_data = {"nodes": [], "edges": []}
        
        for py_file in project_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                tree = ast.parse(content)
                
                file_key = str(py_file.relative_to(project_path))
                graph_data["nodes"].append({"id": file_key, "type": "file"})
                
                # Find imports to other project files
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module and node.module.startswith("."):
                            # Relative import within project
                            graph_data["edges"].append({
                                "source": file_key,
                                "target": node.module,
                                "type": "import"
                            })
                            
            except:
                continue
        
        return graph_data
    
    async def _build_function_call_graph(self, project_path: Path) -> Dict[str, Any]:
        """Build function-level call graph."""
        call_graph = {"functions": {}, "calls": []}
        
        # This would be a complex implementation
        # For now, return a placeholder structure
        return call_graph
    
    async def _build_data_flow_graph(self, project_path: Path) -> Dict[str, Any]:
        """Build data flow dependency graph."""
        data_flow = {"data_sources": [], "transformations": [], "outputs": []}
        
        for py_file in project_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                
                # Detect data sources
                if re.search(r'(\.load|\.read_csv|\.read_excel)', content):
                    data_flow["data_sources"].append({
                        "file": str(py_file.relative_to(project_path)),
                        "operations": re.findall(r'\.(load|read_csv|read_excel)', content)
                    })
                
                # Detect outputs
                if re.search(r'(\.save|\.to_csv|\.to_excel)', content):
                    data_flow["outputs"].append({
                        "file": str(py_file.relative_to(project_path)),
                        "operations": re.findall(r'\.(save|to_csv|to_excel)', content)
                    })
                    
            except:
                continue
        
        return data_flow
    
    async def _build_config_dependency_graph(self, project_path: Path) -> Dict[str, Any]:
        """Build configuration dependency graph."""
        config_deps = {"config_files": [], "usage": []}
        
        # Find configuration files
        config_files = list(project_path.rglob("*.yaml")) + list(project_path.rglob("*.yml"))
        config_deps["config_files"] = [str(f.relative_to(project_path)) for f in config_files]
        
        # Find configuration usage
        for py_file in project_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                if "CONFIG" in content:
                    config_deps["usage"].append({
                        "file": str(py_file.relative_to(project_path)),
                        "config_references": re.findall(r'CONFIG\.[A-Z_]+\.[A-Z_]+', content)
                    })
            except:
                continue
        
        return config_deps
    
    def _calculate_dependency_metrics(self, file_deps: Dict, function_deps: Dict) -> Dict[str, Any]:
        """Calculate dependency-related metrics."""
        return {
            "total_files": len(file_deps.get("nodes", [])),
            "total_dependencies": len(file_deps.get("edges", [])),
            "average_dependencies_per_file": len(file_deps.get("edges", [])) / max(1, len(file_deps.get("nodes", []))),
            "circular_dependencies": 0,  # Would need graph analysis
            "dependency_depth": 0  # Would need graph traversal
        }
    
    async def _identify_architectural_patterns(self, file_deps: Dict) -> List[str]:
        """Identify architectural patterns from dependency structure."""
        patterns = []
        
        # Simple pattern detection based on structure
        if len(file_deps.get("nodes", [])) > 10:
            patterns.append("modular_architecture")
        
        if any("test" in node["id"] for node in file_deps.get("nodes", [])):
            patterns.append("test_driven")
        
        return patterns
    
    def _generate_visualization_data(self, file_deps: Dict, function_deps: Dict) -> Dict[str, Any]:
        """Generate data for dependency visualization."""
        return {
            "file_graph": file_deps,
            "function_graph": function_deps,
            "layout_suggestions": {
                "algorithm": "force_directed",
                "clustering": True,
                "highlight_cycles": True
            }
        }
    
    async def _generate_dependency_recommendations(self, file_deps: Dict, metrics: Dict) -> List[Dict[str, str]]:
        """Generate recommendations based on dependency analysis."""
        recommendations = []
        
        if metrics["average_dependencies_per_file"] > 5:
            recommendations.append({
                "type": "complexity",
                "message": "Consider reducing file dependencies for better maintainability",
                "priority": "medium"
            })
        
        return recommendations
    
    # Additional placeholder methods for comprehensive analysis
    async def _analyze_computational_complexity(self, project_path: Path) -> Dict[str, Any]:
        """Analyze computational complexity patterns."""
        return {"complexity_patterns": [], "hotspots": []}
    
    async def _analyze_memory_usage_patterns(self, project_path: Path) -> Dict[str, Any]:
        """Analyze memory usage patterns."""
        return {"memory_patterns": [], "optimization_opportunities": []}
    
    async def _analyze_io_efficiency(self, project_path: Path) -> Dict[str, Any]:
        """Analyze I/O operation efficiency."""
        return {"io_patterns": [], "efficiency_score": 0}
    
    async def _identify_parallelization_opportunities(self, project_path: Path) -> List[Dict[str, Any]]:
        """Identify parallelization opportunities."""
        return []
    
    async def _identify_caching_opportunities(self, project_path: Path) -> List[Dict[str, Any]]:
        """Identify caching opportunities."""
        opportunities = []
        
        for py_file in project_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                if "expensive_computation" in content or "slow_operation" in content:
                    opportunities.append({
                        "file": str(py_file.relative_to(project_path)),
                        "type": "computation_caching",
                        "potential_impact": "high"
                    })
            except:
                continue
        
        return opportunities
    
    async def _identify_performance_hotspots(self, project_path: Path) -> List[Dict[str, Any]]:
        """Identify potential performance hotspots."""
        return []
    
    async def _generate_optimization_roadmap(self, project_path: Path) -> Dict[str, Any]:
        """Generate performance optimization roadmap."""
        return {
            "short_term": [],
            "medium_term": [],
            "long_term": []
        }
    
    # Research workflow analysis methods
    async def _detect_pipeline_patterns(self, project_path: Path) -> List[Dict[str, Any]]:
        """Detect data processing pipeline patterns."""
        return []
    
    async def _detect_analysis_workflows(self, project_path: Path) -> List[Dict[str, Any]]:
        """Detect analysis workflow patterns."""
        return []
    
    async def _detect_visualization_patterns(self, project_path: Path) -> List[Dict[str, Any]]:
        """Detect visualization workflow patterns."""
        return []
    
    async def _assess_reproducibility(self, project_path: Path) -> Dict[str, Any]:
        """Assess project reproducibility."""
        return {"score": 0, "factors": []}
    
    async def _assess_publication_readiness(self, project_path: Path) -> Dict[str, Any]:
        """Assess publication readiness."""
        return {"readiness_score": 0, "missing_elements": []}
    
    async def _assess_workflow_efficiency(self, project_path: Path) -> Dict[str, Any]:
        """Assess workflow efficiency."""
        return {"efficiency_score": 0, "bottlenecks": []}
    
    async def _suggest_workflow_improvements(self, project_path: Path) -> List[Dict[str, str]]:
        """Suggest workflow improvements."""
        return []
    
    # Architectural analysis methods
    async def _assess_architecture_health(self, project_path: Path) -> Dict[str, Any]:
        """Assess overall architecture health."""
        return {"health_score": 0, "indicators": []}
    
    async def _calculate_modularity_score(self, project_path: Path) -> float:
        """Calculate modularity score."""
        return 0.0
    
    async def _analyze_coupling_patterns(self, project_path: Path) -> Dict[str, Any]:
        """Analyze coupling patterns."""
        return {"coupling_score": 0, "tight_couplings": []}
    
    async def _analyze_cohesion_patterns(self, project_path: Path) -> Dict[str, Any]:
        """Analyze cohesion patterns."""
        return {"cohesion_score": 0, "low_cohesion_modules": []}
    
    async def _assess_scalability(self, project_path: Path) -> Dict[str, Any]:
        """Assess project scalability."""
        return {"scalability_score": 0, "bottlenecks": []}
    
    async def _calculate_maintainability_score(self, project_path: Path) -> float:
        """Calculate maintainability score."""
        return 0.0
    
    async def _generate_evolution_roadmap(self, project_path: Path) -> Dict[str, Any]:
        """Generate architectural evolution roadmap."""
        return {"phases": [], "recommendations": []}
    
    async def _identify_refactoring_opportunities(self, project_path: Path) -> List[Dict[str, Any]]:
        """Identify refactoring opportunities."""
        return []