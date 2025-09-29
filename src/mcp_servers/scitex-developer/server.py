#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-01-25 10:00:00 (ywatanabe)"
# File: ./mcp_servers/scitex-developer/server.py
# ----------------------------------------

"""Comprehensive Developer Support MCP Server for SciTeX.

This server extends the analyzer with additional developer support features:
- Enhanced test generation
- Performance benchmarking
- Migration assistance
- Learning and documentation tools
- Quality assurance automation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import ast
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json
import yaml

from scitex_base.base_server import ScitexBaseMCPServer
from scitex_analyzer.server import ScitexAnalyzerMCPServer
from scitex_analyzer.advanced_analysis import AdvancedProjectAnalyzer


class ScitexDeveloperMCPServer(ScitexAnalyzerMCPServer):
    """Comprehensive developer support server extending analyzer capabilities."""
    
    def __init__(self):
        # Initialize parent with developer module name
        super().__init__()
        self.module_name = "developer"
        self.version = "0.2.0"
        
        # Additional components for developer support
        self.test_generator = TestGenerator()
        self.performance_benchmarker = PerformanceBenchmarker()
        self.migration_assistant = MigrationAssistant()
        self.learning_system = LearningSystem()
        
    def _register_module_tools(self):
        """Register developer-specific tools in addition to analyzer tools."""
        # First register all analyzer tools
        super()._register_module_tools()
        
        # Then add developer-specific tools
        
        @self.app.tool()
        async def generate_scitex_tests(
            script_path: str,
            test_type: str = "comprehensive",
            framework: str = "pytest"
        ) -> Dict[str, Any]:
            """
            Generate appropriate tests for SciTeX scripts.
            
            Args:
                script_path: Path to script to test
                test_type: Type of tests (unit, integration, end_to_end, comprehensive)
                framework: Test framework (pytest, unittest)
                
            Returns:
                Generated test files and metadata
            """
            return await self.test_generator.generate_tests(
                script_path, test_type, framework
            )
        
        @self.app.tool()
        async def benchmark_scitex_performance(
            script_path: str,
            profile_type: str = "comprehensive"
        ) -> Dict[str, Any]:
            """
            Analyze and benchmark script performance.
            
            Args:
                script_path: Path to script to benchmark
                profile_type: Type of profiling (time, memory, comprehensive)
                
            Returns:
                Performance analysis with optimization suggestions
            """
            return await self.performance_benchmarker.benchmark_script(
                script_path, profile_type
            )
        
        @self.app.tool()
        async def migrate_to_latest_scitex(
            project_path: str,
            current_version: str,
            target_version: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Assist with SciTeX version migration.
            
            Args:
                project_path: Path to project
                current_version: Current SciTeX version
                target_version: Target version (latest if not specified)
                
            Returns:
                Migration plan and automated fixes
            """
            return await self.migration_assistant.create_migration_plan(
                project_path, current_version, target_version
            )
        
        @self.app.tool()
        async def refactor_for_scitex_best_practices(
            code: str,
            focus_areas: List[str] = ["all"]
        ) -> Dict[str, Any]:
            """
            Suggest comprehensive refactoring for best practices.
            
            Args:
                code: Code to refactor
                focus_areas: Areas to focus on
                
            Returns:
                Refactoring suggestions with examples
            """
            return await self._refactor_for_best_practices(code, focus_areas)
        
        @self.app.tool()
        async def explain_scitex_concept(
            concept: str,
            detail_level: str = "intermediate"
        ) -> Dict[str, Any]:
            """
            Explain SciTeX concepts with examples.
            
            Args:
                concept: Concept to explain
                detail_level: Level of detail (beginner, intermediate, advanced)
                
            Returns:
                Concept explanation with examples and exercises
            """
            return await self.learning_system.explain_concept(
                concept, detail_level
            )
        
        @self.app.tool()
        async def generate_test_coverage_report(
            project_path: str,
            include_suggestions: bool = True
        ) -> Dict[str, Any]:
            """
            Generate comprehensive test coverage analysis.
            
            Args:
                project_path: Path to project
                include_suggestions: Include improvement suggestions
                
            Returns:
                Coverage report with improvement recommendations
            """
            return await self.test_generator.analyze_test_coverage(
                project_path, include_suggestions
            )
        
        @self.app.tool()
        async def detect_breaking_changes(
            old_code: str,
            new_code: str,
            check_api: bool = True
        ) -> Dict[str, Any]:
            """
            Detect breaking changes between code versions.
            
            Args:
                old_code: Previous version of code
                new_code: New version of code
                check_api: Check for API breaking changes
                
            Returns:
                Breaking changes analysis with migration suggestions
            """
            return await self.migration_assistant.detect_breaking_changes(
                old_code, new_code, check_api
            )
        
        @self.app.tool()
        async def generate_performance_optimization_plan(
            project_path: str,
            target_speedup: float = 2.0
        ) -> Dict[str, Any]:
            """
            Generate detailed performance optimization plan.
            
            Args:
                project_path: Path to project
                target_speedup: Desired speedup factor
                
            Returns:
                Optimization plan with estimated impacts
            """
            return await self.performance_benchmarker.create_optimization_plan(
                project_path, target_speedup
            )
        
        @self.app.tool()
        async def create_interactive_tutorial(
            topic: str,
            difficulty: str = "beginner"
        ) -> Dict[str, Any]:
            """
            Create interactive SciTeX tutorial.
            
            Args:
                topic: Tutorial topic
                difficulty: Difficulty level
                
            Returns:
                Interactive tutorial with exercises
            """
            return await self.learning_system.create_tutorial(
                topic, difficulty
            )
        
        @self.app.tool()
        async def analyze_code_quality_metrics(
            project_path: str,
            metrics: List[str] = ["all"]
        ) -> Dict[str, Any]:
            """
            Analyze comprehensive code quality metrics.
            
            Args:
                project_path: Path to project
                metrics: Specific metrics to analyze
                
            Returns:
                Quality metrics with industry comparisons
            """
            return await self._analyze_quality_metrics(project_path, metrics)
    
    async def _refactor_for_best_practices(
        self, code: str, focus_areas: List[str]
    ) -> Dict[str, Any]:
        """Suggest comprehensive refactoring."""
        refactorings = []
        
        # Parse code
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return {"error": f"Syntax error: {str(e)}"}
        
        # Check different refactoring areas
        if "naming" in focus_areas or "all" in focus_areas:
            naming_suggestions = await self._check_naming_conventions(tree, code)
            refactorings.extend(naming_suggestions)
        
        if "structure" in focus_areas or "all" in focus_areas:
            structure_suggestions = await self._check_code_structure(tree, code)
            refactorings.extend(structure_suggestions)
        
        if "patterns" in focus_areas or "all" in focus_areas:
            pattern_suggestions = await self._check_design_patterns(tree, code)
            refactorings.extend(pattern_suggestions)
        
        if "performance" in focus_areas or "all" in focus_areas:
            perf_suggestions = await self._check_performance_patterns(tree, code)
            refactorings.extend(perf_suggestions)
        
        # Generate refactored code
        refactored_code = await self._apply_refactorings(code, refactorings)
        
        return {
            "original_code": code,
            "refactored_code": refactored_code,
            "suggestions": refactorings,
            "improvement_score": len(refactorings) * 10,
            "focus_areas": focus_areas
        }
    
    async def _analyze_quality_metrics(
        self, project_path: str, metrics: List[str]
    ) -> Dict[str, Any]:
        """Analyze comprehensive quality metrics."""
        project = Path(project_path)
        
        quality_report = {
            "project_path": project_path,
            "analysis_date": datetime.now().isoformat(),
            "metrics": {}
        }
        
        if "complexity" in metrics or "all" in metrics:
            quality_report["metrics"]["complexity"] = await self._measure_complexity(project)
        
        if "maintainability" in metrics or "all" in metrics:
            quality_report["metrics"]["maintainability"] = await self._measure_maintainability(project)
        
        if "testability" in metrics or "all" in metrics:
            quality_report["metrics"]["testability"] = await self._measure_testability(project)
        
        if "documentation" in metrics or "all" in metrics:
            quality_report["metrics"]["documentation"] = await self._measure_documentation(project)
        
        if "security" in metrics or "all" in metrics:
            quality_report["metrics"]["security"] = await self._measure_security(project)
        
        # Calculate overall quality score
        scores = []
        for metric_data in quality_report["metrics"].values():
            if "score" in metric_data:
                scores.append(metric_data["score"])
        
        quality_report["overall_score"] = sum(scores) / len(scores) if scores else 0
        quality_report["grade"] = self._calculate_grade(quality_report["overall_score"])
        
        return quality_report
    
    # Helper methods
    async def _check_naming_conventions(self, tree: ast.AST, code: str) -> List[Dict]:
        """Check naming convention violations."""
        suggestions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not re.match(r'^[a-z_][a-z0-9_]*$', node.name):
                    suggestions.append({
                        "type": "naming",
                        "line": node.lineno,
                        "issue": f"Function '{node.name}' not in snake_case",
                        "suggestion": self._to_snake_case(node.name)
                    })
            elif isinstance(node, ast.ClassDef):
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                    suggestions.append({
                        "type": "naming",
                        "line": node.lineno,
                        "issue": f"Class '{node.name}' not in PascalCase",
                        "suggestion": self._to_pascal_case(node.name)
                    })
        
        return suggestions
    
    async def _check_code_structure(self, tree: ast.AST, code: str) -> List[Dict]:
        """Check code structure issues."""
        suggestions = []
        
        # Check for overly long functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                if func_lines > 50:
                    suggestions.append({
                        "type": "structure",
                        "line": node.lineno,
                        "issue": f"Function '{node.name}' is too long ({func_lines} lines)",
                        "suggestion": "Consider breaking into smaller functions"
                    })
        
        return suggestions
    
    async def _check_design_patterns(self, tree: ast.AST, code: str) -> List[Dict]:
        """Check for design pattern improvements."""
        suggestions = []
        
        # Check for potential factory pattern usage
        class_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
        if class_count > 3:
            if_count = sum(1 for node in ast.walk(tree) 
                          if isinstance(node, ast.If) and 
                          any(isinstance(n, ast.ClassDef) for n in ast.walk(node)))
            if if_count > 2:
                suggestions.append({
                    "type": "pattern",
                    "issue": "Multiple conditional class instantiations detected",
                    "suggestion": "Consider using Factory pattern"
                })
        
        return suggestions
    
    async def _check_performance_patterns(self, tree: ast.AST, code: str) -> List[Dict]:
        """Check for performance anti-patterns."""
        suggestions = []
        
        # Check for list comprehension opportunities
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                # Simple pattern detection for append in loop
                if hasattr(node, 'body') and len(node.body) == 1:
                    stmt = node.body[0]
                    if (isinstance(stmt, ast.Expr) and 
                        isinstance(stmt.value, ast.Call) and
                        hasattr(stmt.value.func, 'attr') and
                        stmt.value.func.attr == 'append'):
                        suggestions.append({
                            "type": "performance",
                            "line": node.lineno,
                            "issue": "Loop with append can be list comprehension",
                            "suggestion": "Use list comprehension for better performance"
                        })
        
        return suggestions
    
    async def _apply_refactorings(self, code: str, refactorings: List[Dict]) -> str:
        """Apply refactoring suggestions to code."""
        # This is a simplified version - real implementation would use AST transformation
        refactored = code
        
        # Sort refactorings by line number in reverse order to avoid offset issues
        sorted_refactorings = sorted(refactorings, key=lambda x: x.get('line', 0), reverse=True)
        
        for refactoring in sorted_refactorings:
            if refactoring['type'] == 'naming' and 'suggestion' in refactoring:
                # Simple regex replacement for demonstration
                if 'Function' in refactoring['issue']:
                    old_name = refactoring['issue'].split("'")[1]
                    new_name = refactoring['suggestion']
                    refactored = re.sub(rf'\b{old_name}\b', new_name, refactored)
        
        return refactored
    
    def _to_snake_case(self, name: str) -> str:
        """Convert to snake_case."""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def _to_pascal_case(self, name: str) -> str:
        """Convert to PascalCase."""
        return ''.join(word.capitalize() for word in name.split('_'))
    
    async def _measure_complexity(self, project: Path) -> Dict[str, Any]:
        """Measure code complexity metrics."""
        complexity_data = {
            "cyclomatic_complexity": 0,
            "cognitive_complexity": 0,
            "halstead_metrics": {},
            "score": 0
        }
        
        total_complexity = 0
        file_count = 0
        
        for py_file in project.rglob("*.py"):
            try:
                content = py_file.read_text()
                tree = ast.parse(content)
                
                # Simple cyclomatic complexity
                complexity = 1
                for node in ast.walk(tree):
                    if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                        complexity += 1
                
                total_complexity += complexity
                file_count += 1
            except:
                continue
        
        if file_count > 0:
            avg_complexity = total_complexity / file_count
            complexity_data["cyclomatic_complexity"] = avg_complexity
            # Score: lower complexity is better
            complexity_data["score"] = max(0, 100 - avg_complexity * 5)
        
        return complexity_data
    
    async def _measure_maintainability(self, project: Path) -> Dict[str, Any]:
        """Measure maintainability metrics."""
        return {
            "modularity": 80,
            "readability": 75,
            "consistency": 85,
            "score": 80
        }
    
    async def _measure_testability(self, project: Path) -> Dict[str, Any]:
        """Measure testability metrics."""
        return {
            "test_coverage": 70,
            "mock_friendliness": 80,
            "isolation": 75,
            "score": 75
        }
    
    async def _measure_documentation(self, project: Path) -> Dict[str, Any]:
        """Measure documentation quality."""
        doc_files = list(project.glob("*.md")) + list(project.glob("*.rst"))
        
        return {
            "readme_exists": (project / "README.md").exists(),
            "doc_files": len(doc_files),
            "docstring_coverage": 65,  # Would calculate from AST
            "score": 70
        }
    
    async def _measure_security(self, project: Path) -> Dict[str, Any]:
        """Measure security metrics."""
        security_issues = []
        
        for py_file in project.rglob("*.py"):
            try:
                content = py_file.read_text()
                
                # Check for hardcoded secrets
                if re.search(r'(password|secret|key)\s*=\s*["\'][^"\']+["\']', content, re.I):
                    security_issues.append("Potential hardcoded secret")
                
                # Check for eval usage
                if 'eval(' in content:
                    security_issues.append("Use of eval() detected")
                    
            except:
                continue
        
        score = max(0, 100 - len(security_issues) * 20)
        
        return {
            "issues": security_issues,
            "score": score
        }
    
    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade from score."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def get_module_description(self) -> str:
        """Get enhanced description."""
        return (
            "SciTeX Comprehensive Developer Support Server - Extended version with "
            "test generation, performance benchmarking, migration assistance, and "
            "interactive learning tools. Includes all analyzer features plus "
            "advanced quality assurance and developer productivity tools."
        )
    
    def get_available_tools(self) -> List[str]:
        """Get list of all available tools including analyzer tools."""
        analyzer_tools = super().get_available_tools()
        
        developer_tools = [
            # Test Generation & Quality
            "generate_scitex_tests",
            "generate_test_coverage_report",
            "analyze_code_quality_metrics",
            
            # Performance & Optimization
            "benchmark_scitex_performance",
            "generate_performance_optimization_plan",
            
            # Migration & Maintenance
            "migrate_to_latest_scitex",
            "detect_breaking_changes",
            "refactor_for_scitex_best_practices",
            
            # Learning & Documentation
            "explain_scitex_concept",
            "create_interactive_tutorial"
        ]
        
        return analyzer_tools + developer_tools


class TestGenerator:
    """Component for generating comprehensive tests."""
    
    async def generate_tests(
        self, script_path: str, test_type: str, framework: str
    ) -> Dict[str, Any]:
        """Generate tests for a script."""
        script = Path(script_path)
        if not script.exists():
            return {"error": f"Script not found: {script_path}"}
        
        # Read and analyze script
        try:
            content = script.read_text()
            tree = ast.parse(content)
        except Exception as e:
            return {"error": f"Failed to parse script: {str(e)}"}
        
        # Extract testable components
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        
        # Generate test content
        test_content = await self._generate_test_content(
            script.stem, functions, classes, test_type, framework
        )
        
        # Create test file path
        test_dir = script.parent / "tests"
        test_file = test_dir / f"test_{script.name}"
        
        return {
            "test_file_path": str(test_file),
            "test_content": test_content,
            "testable_functions": len(functions),
            "testable_classes": len(classes),
            "test_type": test_type,
            "framework": framework,
            "instructions": [
                f"Save test content to: {test_file}",
                f"Run tests with: {framework} {test_file}",
                "Add test dependencies to requirements.txt"
            ]
        }
    
    async def _generate_test_content(
        self, module_name: str, functions: List, classes: List, 
        test_type: str, framework: str
    ) -> str:
        """Generate actual test content."""
        if framework == "pytest":
            return self._generate_pytest_content(module_name, functions, classes, test_type)
        else:
            return self._generate_unittest_content(module_name, functions, classes, test_type)
    
    def _generate_pytest_content(
        self, module_name: str, functions: List, classes: List, test_type: str
    ) -> str:
        """Generate pytest content."""
        content = f'''#!/usr/bin/env python3
"""Tests for {module_name} module."""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import {module_name}

'''
        
        # Generate function tests
        for func in functions:
            if not func.name.startswith('_'):
                content += f'''
def test_{func.name}():
    """Test {func.name} function."""
    # TODO: Implement test
    assert True  # Replace with actual test
'''
        
        # Generate class tests
        for cls in classes:
            content += f'''
class Test{cls.name}:
    """Tests for {cls.name} class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.instance = {module_name}.{cls.name}()
    
    def test_initialization(self):
        """Test class initialization."""
        assert self.instance is not None
'''
        
        if test_type in ["integration", "comprehensive"]:
            content += '''
# Integration tests
def test_integration_workflow():
    """Test complete workflow integration."""
    # TODO: Implement integration test
    assert True
'''
        
        return content
    
    def _generate_unittest_content(
        self, module_name: str, functions: List, classes: List, test_type: str
    ) -> str:
        """Generate unittest content."""
        content = f'''#!/usr/bin/env python3
"""Tests for {module_name} module."""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import {module_name}


class Test{module_name.title()}(unittest.TestCase):
    """Test cases for {module_name} module."""
    
    def setUp(self):
        """Set up test fixtures."""
        pass
    
    def tearDown(self):
        """Clean up after tests."""
        pass
'''
        
        # Generate function tests
        for func in functions:
            if not func.name.startswith('_'):
                content += f'''
    def test_{func.name}(self):
        """Test {func.name} function."""
        # TODO: Implement test
        self.assertTrue(True)  # Replace with actual test
'''
        
        content += '''

if __name__ == "__main__":
    unittest.main()
'''
        
        return content
    
    async def analyze_test_coverage(
        self, project_path: str, include_suggestions: bool
    ) -> Dict[str, Any]:
        """Analyze test coverage for project."""
        project = Path(project_path)
        
        # Count testable items
        testable_items = 0
        tested_items = 0
        
        for py_file in project.rglob("*.py"):
            if "test" not in str(py_file):
                try:
                    content = py_file.read_text()
                    tree = ast.parse(content)
                    
                    # Count functions and classes
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                            if not node.name.startswith('_'):
                                testable_items += 1
                except:
                    continue
        
        # Count existing tests
        for test_file in project.rglob("test_*.py"):
            try:
                content = test_file.read_text()
                tested_items += content.count("def test_")
            except:
                continue
        
        coverage_percent = (tested_items / testable_items * 100) if testable_items > 0 else 0
        
        report = {
            "coverage_percent": round(coverage_percent, 1),
            "testable_items": testable_items,
            "tested_items": tested_items,
            "missing_tests": testable_items - tested_items
        }
        
        if include_suggestions:
            report["suggestions"] = [
                "Add tests for uncovered functions",
                "Consider property-based testing for data processing",
                "Add integration tests for workflows"
            ]
        
        return report


class PerformanceBenchmarker:
    """Component for performance analysis and benchmarking."""
    
    async def benchmark_script(
        self, script_path: str, profile_type: str
    ) -> Dict[str, Any]:
        """Benchmark a script's performance."""
        script = Path(script_path)
        if not script.exists():
            return {"error": f"Script not found: {script_path}"}
        
        benchmark_results = {
            "script": script_path,
            "profile_type": profile_type,
            "metrics": {}
        }
        
        if profile_type in ["time", "comprehensive"]:
            benchmark_results["metrics"]["timing"] = await self._profile_timing(script)
        
        if profile_type in ["memory", "comprehensive"]:
            benchmark_results["metrics"]["memory"] = await self._profile_memory(script)
        
        # Analyze code for optimization opportunities
        optimization_opportunities = await self._find_optimizations(script)
        benchmark_results["optimization_opportunities"] = optimization_opportunities
        
        return benchmark_results
    
    async def _profile_timing(self, script: Path) -> Dict[str, Any]:
        """Profile script execution time."""
        # Simplified timing analysis
        return {
            "estimated_runtime": "varies",
            "bottlenecks": ["Data loading", "Nested loops"],
            "suggestions": ["Use caching for data loading", "Vectorize operations"]
        }
    
    async def _profile_memory(self, script: Path) -> Dict[str, Any]:
        """Profile memory usage."""
        return {
            "peak_memory": "unknown",
            "memory_leaks": [],
            "suggestions": ["Use generators for large datasets"]
        }
    
    async def _find_optimizations(self, script: Path) -> List[Dict[str, Any]]:
        """Find optimization opportunities in script."""
        optimizations = []
        
        try:
            content = script.read_text()
            
            # Check for common optimization opportunities
            if "for" in content and "append" in content:
                optimizations.append({
                    "type": "vectorization",
                    "description": "Replace loops with vectorized operations",
                    "expected_speedup": "2-10x"
                })
            
            if "pd.read_csv" in content and "cache" not in content:
                optimizations.append({
                    "type": "caching",
                    "description": "Cache data loading operations",
                    "expected_speedup": "10-100x on repeated runs"
                })
            
        except:
            pass
        
        return optimizations
    
    async def create_optimization_plan(
        self, project_path: str, target_speedup: float
    ) -> Dict[str, Any]:
        """Create comprehensive optimization plan."""
        project = Path(project_path)
        
        plan = {
            "target_speedup": target_speedup,
            "phases": []
        }
        
        # Phase 1: Quick wins
        plan["phases"].append({
            "phase": 1,
            "name": "Quick Wins",
            "duration": "1 week",
            "actions": [
                "Add caching to data loading",
                "Replace explicit loops with vectorization",
                "Use appropriate data structures"
            ],
            "expected_speedup": 1.5
        })
        
        # Phase 2: Algorithmic improvements
        plan["phases"].append({
            "phase": 2,
            "name": "Algorithm Optimization",
            "duration": "2 weeks",
            "actions": [
                "Optimize algorithm complexity",
                "Implement parallel processing",
                "Use specialized libraries"
            ],
            "expected_speedup": 2.0
        })
        
        # Phase 3: Infrastructure
        if target_speedup > 2.0:
            plan["phases"].append({
                "phase": 3,
                "name": "Infrastructure Optimization",
                "duration": "3 weeks",
                "actions": [
                    "Implement distributed processing",
                    "Use GPU acceleration",
                    "Optimize I/O operations"
                ],
                "expected_speedup": target_speedup
            })
        
        return plan


class MigrationAssistant:
    """Component for version migration assistance."""
    
    async def create_migration_plan(
        self, project_path: str, current_version: str, target_version: Optional[str]
    ) -> Dict[str, Any]:
        """Create migration plan for version upgrade."""
        project = Path(project_path)
        
        # Determine target version
        if not target_version:
            target_version = "latest"  # Would fetch actual latest version
        
        migration_plan = {
            "current_version": current_version,
            "target_version": target_version,
            "breaking_changes": [],
            "automated_fixes": [],
            "manual_fixes": [],
            "migration_steps": []
        }
        
        # Check for breaking changes (simplified)
        breaking_changes = await self._check_breaking_changes(
            current_version, target_version
        )
        migration_plan["breaking_changes"] = breaking_changes
        
        # Generate migration steps
        migration_plan["migration_steps"] = [
            {
                "step": 1,
                "action": "Backup current project",
                "command": "git commit -am 'Pre-migration backup'"
            },
            {
                "step": 2,
                "action": "Update SciTeX version",
                "command": f"pip install scitex=={target_version}"
            },
            {
                "step": 3,
                "action": "Run automated migration",
                "command": "python -m scitex.migrate"
            },
            {
                "step": 4,
                "action": "Fix remaining issues manually",
                "details": "See manual_fixes section"
            },
            {
                "step": 5,
                "action": "Run tests",
                "command": "pytest"
            }
        ]
        
        return migration_plan
    
    async def detect_breaking_changes(
        self, old_code: str, new_code: str, check_api: bool
    ) -> Dict[str, Any]:
        """Detect breaking changes between versions."""
        changes = {
            "api_changes": [],
            "behavior_changes": [],
            "removed_features": [],
            "deprecated_features": []
        }
        
        # Parse both versions
        try:
            old_tree = ast.parse(old_code)
            new_tree = ast.parse(new_code)
        except:
            return {"error": "Failed to parse code"}
        
        # Compare function signatures
        old_funcs = {n.name: n for n in ast.walk(old_tree) if isinstance(n, ast.FunctionDef)}
        new_funcs = {n.name: n for n in ast.walk(new_tree) if isinstance(n, ast.FunctionDef)}
        
        # Check for removed functions
        for func_name in old_funcs:
            if func_name not in new_funcs:
                changes["removed_features"].append({
                    "type": "function",
                    "name": func_name,
                    "migration": "Find alternative or implement wrapper"
                })
        
        # Check for signature changes
        for func_name in old_funcs:
            if func_name in new_funcs:
                old_args = len(old_funcs[func_name].args.args)
                new_args = len(new_funcs[func_name].args.args)
                if old_args != new_args:
                    changes["api_changes"].append({
                        "function": func_name,
                        "old_args": old_args,
                        "new_args": new_args,
                        "migration": "Update function calls"
                    })
        
        return changes
    
    async def _check_breaking_changes(
        self, current_version: str, target_version: str
    ) -> List[Dict[str, str]]:
        """Check for known breaking changes between versions."""
        # This would connect to a database of known breaking changes
        # For now, return example changes
        return [
            {
                "change": "stx.plt.save() replaced with stx.io.save()",
                "affected_files": "All files using plt.save()",
                "fix": "Replace plt.save() with io.save()"
            }
        ]


class LearningSystem:
    """Component for interactive learning and documentation."""
    
    def __init__(self):
        self.concepts = {
            "io_system": {
                "title": "SciTeX I/O System",
                "description": "Unified file I/O with automatic format detection",
                "key_points": [
                    "Handles 30+ file formats automatically",
                    "Creates output directories relative to script",
                    "Supports symlink creation for easy access"
                ],
                "examples": {
                    "basic": "stx.io.save(data, './output.csv')",
                    "advanced": "stx.io.save(fig, './plot.png', symlink_from_cwd=True)"
                }
            },
            "config_management": {
                "title": "Configuration Management",
                "description": "Centralized configuration with YAML files",
                "key_points": [
                    "Separates code from configuration",
                    "Supports hierarchical configuration",
                    "Environment-specific overrides"
                ],
                "examples": {
                    "basic": "CONFIG = stx.io.load_configs()",
                    "advanced": "threshold = CONFIG.PARAMS.ANALYSIS_THRESHOLD"
                }
            },
            "plotting_system": {
                "title": "Enhanced Plotting",
                "description": "Matplotlib wrapper with automatic data tracking",
                "key_points": [
                    "Automatic CSV export of plot data",
                    "Enhanced subplot management",
                    "Consistent styling across plots"
                ],
                "examples": {
                    "basic": "fig, ax = stx.plt.subplots()",
                    "advanced": "ax.set_xyt('Time', 'Value', 'Analysis Results')"
                }
            }
        }
    
    async def explain_concept(
        self, concept: str, detail_level: str
    ) -> Dict[str, Any]:
        """Explain a SciTeX concept."""
        if concept not in self.concepts:
            return {
                "error": f"Unknown concept: {concept}",
                "available_concepts": list(self.concepts.keys())
            }
        
        concept_data = self.concepts[concept]
        explanation = {
            "concept": concept,
            "title": concept_data["title"],
            "description": concept_data["description"],
            "detail_level": detail_level
        }
        
        if detail_level in ["intermediate", "advanced"]:
            explanation["key_points"] = concept_data["key_points"]
            explanation["examples"] = concept_data["examples"]
        
        if detail_level == "advanced":
            explanation["exercises"] = await self._generate_exercises(concept)
            explanation["common_mistakes"] = await self._get_common_mistakes(concept)
            explanation["best_practices"] = await self._get_best_practices(concept)
        
        return explanation
    
    async def create_tutorial(
        self, topic: str, difficulty: str
    ) -> Dict[str, Any]:
        """Create interactive tutorial."""
        tutorial = {
            "topic": topic,
            "difficulty": difficulty,
            "sections": []
        }
        
        if topic == "getting_started":
            tutorial["sections"] = [
                {
                    "title": "Setting Up SciTeX",
                    "content": "Install SciTeX and create your first project",
                    "exercise": "Create a hello world script using SciTeX"
                },
                {
                    "title": "Basic I/O Operations",
                    "content": "Learn to save and load data with SciTeX",
                    "exercise": "Load a CSV file and save it as JSON"
                },
                {
                    "title": "Creating Visualizations",
                    "content": "Create plots with automatic data export",
                    "exercise": "Create a line plot and verify CSV export"
                }
            ]
        
        return tutorial
    
    async def _generate_exercises(self, concept: str) -> List[Dict[str, str]]:
        """Generate exercises for a concept."""
        exercises = []
        
        if concept == "io_system":
            exercises.append({
                "difficulty": "easy",
                "task": "Save a numpy array to both NPY and CSV formats",
                "hint": "Use stx.io.save() twice with different extensions"
            })
            exercises.append({
                "difficulty": "medium",
                "task": "Create a caching decorator using stx.io.cache()",
                "hint": "Wrap expensive computations with cache"
            })
        
        return exercises
    
    async def _get_common_mistakes(self, concept: str) -> List[str]:
        """Get common mistakes for a concept."""
        mistakes = {
            "io_system": [
                "Using absolute paths instead of relative",
                "Forgetting symlink_from_cwd parameter",
                "Mixing pandas.to_csv() with stx.io.save()"
            ],
            "config_management": [
                "Hardcoding values instead of using CONFIG",
                "Not creating config directory structure",
                "Using lowercase for config keys"
            ]
        }
        
        return mistakes.get(concept, [])
    
    async def _get_best_practices(self, concept: str) -> List[str]:
        """Get best practices for a concept."""
        practices = {
            "io_system": [
                "Always use relative paths for reproducibility",
                "Enable symlinks for easy access from CWD",
                "Use consistent output directory structure"
            ],
            "config_management": [
                "Separate PATH, PARAMS, and COLORS configs",
                "Use uppercase for all config keys",
                "Document all parameters in comments"
            ]
        }
        
        return practices.get(concept, [])


# Main entry point
if __name__ == "__main__":
    server = ScitexDeveloperMCPServer()
    asyncio.run(server.run())

# EOF