#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-09 20:52:00"
# File: /project_management/test_quality_metrics.py
# ----------------------------------------
"""
Test Quality Metrics Analyzer for SciTeX Project

This script analyzes test files to measure quality metrics:
- Use of advanced testing patterns (fixtures, mocks, property-based)
- Edge case coverage
- Performance testing
- Test documentation quality
- Code-to-test ratio
"""

import os
import ast
import re
from pathlib import Path
from collections import defaultdict
import json


class TestQualityAnalyzer:
    """Analyzes test files for quality metrics."""
    
    def __init__(self, test_dir="tests", src_dir="src"):
        self.test_dir = Path(test_dir)
        self.src_dir = Path(src_dir)
        self.metrics = defaultdict(lambda: defaultdict(int))
        
    def analyze_all_tests(self):
        """Analyze all test files in the test directory."""
        test_files = list(self.test_dir.rglob("test_*.py"))
        
        print(f"Found {len(test_files)} test files to analyze")
        
        for test_file in test_files:
            if "__pycache__" in str(test_file):
                continue
            self.analyze_test_file(test_file)
        
        return self.generate_report()
    
    def analyze_test_file(self, filepath):
        """Analyze a single test file for quality metrics."""
        module_name = self._get_module_name(filepath)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)
        except Exception as e:
            print(f"Error parsing {filepath}: {e}")
            return
        
        # Basic metrics
        self.metrics[module_name]['total_files'] += 1
        self.metrics[module_name]['total_lines'] += len(content.splitlines())
        
        # Analyze patterns
        self._analyze_fixtures(tree, content, module_name)
        self._analyze_mocking(content, module_name)
        self._analyze_property_testing(content, module_name)
        self._analyze_parametrized_tests(tree, module_name)
        self._analyze_edge_cases(content, module_name)
        self._analyze_performance_tests(tree, content, module_name)
        self._analyze_error_handling(tree, content, module_name)
        self._analyze_documentation(tree, module_name)
        self._count_test_functions(tree, module_name)
        
    def _get_module_name(self, filepath):
        """Extract module name from file path."""
        parts = filepath.parts
        if 'scitex' in parts:
            idx = parts.index('scitex')
            return '.'.join(parts[idx:-1])
        return 'unknown'
    
    def _analyze_fixtures(self, tree, content, module):
        """Count fixture usage."""
        fixture_count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for @pytest.fixture decorator
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name) and decorator.id == 'fixture':
                        fixture_count += 1
                    elif isinstance(decorator, ast.Attribute) and decorator.attr == 'fixture':
                        fixture_count += 1
        
        # Also check for fixture usage in function parameters
        fixture_usage = len(re.findall(r'def test_\w+\([^)]*\w+[^)]*\)', content))
        
        self.metrics[module]['fixtures_defined'] += fixture_count
        self.metrics[module]['fixtures_used'] += fixture_usage
    
    def _analyze_mocking(self, content, module):
        """Count mock usage."""
        mock_patterns = [
            r'from unittest\.mock import',
            r'@patch\(',
            r'@mock\.',
            r'Mock\(',
            r'MagicMock\(',
            r'mock_\w+',
            r'\.assert_called',
        ]
        
        mock_count = sum(len(re.findall(pattern, content)) for pattern in mock_patterns)
        self.metrics[module]['mock_usage'] += mock_count
    
    def _analyze_property_testing(self, content, module):
        """Check for property-based testing."""
        property_patterns = [
            r'from hypothesis import',
            r'@given\(',
            r'strategies\.',
            r'@hypothesis\.',
        ]
        
        property_count = sum(len(re.findall(pattern, content)) for pattern in property_patterns)
        self.metrics[module]['property_tests'] += property_count
    
    def _analyze_parametrized_tests(self, tree, module):
        """Count parametrized tests."""
        param_count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        if hasattr(decorator.func, 'attr') and decorator.func.attr == 'parametrize':
                            param_count += 1
        
        self.metrics[module]['parametrized_tests'] += param_count
    
    def _analyze_edge_cases(self, content, module):
        """Detect edge case testing."""
        edge_patterns = [
            r'empty',
            r'null|none',
            r'zero',
            r'negative',
            r'boundary',
            r'overflow',
            r'special.?char',
            r'unicode',
            r'large',
            r'tiny',
            r'edge.?case',
            r'corner.?case',
            r'limit',
        ]
        
        edge_count = sum(len(re.findall(pattern, content, re.I)) for pattern in edge_patterns)
        self.metrics[module]['edge_case_tests'] += edge_count
    
    def _analyze_performance_tests(self, tree, content, module):
        """Count performance-related tests."""
        perf_patterns = [
            r'@pytest\.mark\.benchmark',
            r'benchmark\(',
            r'time\.time\(',
            r'timeit',
            r'performance',
            r'scaling',
            r'memory.?usage',
            r'profile',
        ]
        
        perf_count = sum(len(re.findall(pattern, content, re.I)) for pattern in perf_patterns)
        self.metrics[module]['performance_tests'] += perf_count
    
    def _analyze_error_handling(self, tree, content, module):
        """Count error handling tests."""
        error_count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.With):
                # Check for pytest.raises context manager
                for item in node.items:
                    if isinstance(item.context_expr, ast.Call):
                        if hasattr(item.context_expr.func, 'attr'):
                            if item.context_expr.func.attr == 'raises':
                                error_count += 1
        
        # Also check for assertRaises patterns
        error_count += len(re.findall(r'assertRaises|with pytest\.raises', content))
        
        self.metrics[module]['error_handling_tests'] += error_count
    
    def _analyze_documentation(self, tree, module):
        """Analyze test documentation quality."""
        documented_tests = 0
        total_tests = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                total_tests += 1
                if ast.get_docstring(node):
                    documented_tests += 1
        
        self.metrics[module]['documented_tests'] += documented_tests
        self.metrics[module]['total_test_functions'] += total_tests
    
    def _count_test_functions(self, tree, module):
        """Count different types of test functions."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith('test_'):
                    self.metrics[module]['test_functions'] += 1
                elif node.name.startswith('_'):
                    self.metrics[module]['helper_functions'] += 1
    
    def generate_report(self):
        """Generate quality metrics report."""
        report = {
            'summary': {
                'total_modules': len(self.metrics),
                'total_test_files': sum(m['total_files'] for m in self.metrics.values()),
                'total_test_lines': sum(m['total_lines'] for m in self.metrics.values()),
                'total_test_functions': sum(m['test_functions'] for m in self.metrics.values()),
            },
            'quality_scores': {},
            'module_details': {}
        }
        
        # Calculate quality scores for each module
        for module, metrics in self.metrics.items():
            quality_score = self._calculate_quality_score(metrics)
            report['quality_scores'][module] = quality_score
            report['module_details'][module] = dict(metrics)
        
        # Add overall statistics
        all_scores = list(report['quality_scores'].values())
        if all_scores:
            report['summary']['average_quality_score'] = sum(all_scores) / len(all_scores)
            report['summary']['highest_quality_module'] = max(
                report['quality_scores'].items(), key=lambda x: x[1]
            )
            report['summary']['lowest_quality_module'] = min(
                report['quality_scores'].items(), key=lambda x: x[1]
            )
        
        # Identify modules needing improvement
        report['needs_improvement'] = [
            module for module, score in report['quality_scores'].items()
            if score < 50
        ]
        
        return report
    
    def _calculate_quality_score(self, metrics):
        """Calculate a quality score from 0-100 based on metrics."""
        if metrics['test_functions'] == 0:
            return 0
        
        scores = []
        
        # Fixture usage (max 15 points)
        fixture_score = min(15, (metrics['fixtures_defined'] + metrics['fixtures_used']) * 2)
        scores.append(fixture_score)
        
        # Mock usage (max 15 points)
        mock_score = min(15, metrics['mock_usage'] * 3)
        scores.append(mock_score)
        
        # Property testing (max 10 points)
        property_score = min(10, metrics['property_tests'] * 5)
        scores.append(property_score)
        
        # Parametrized tests (max 10 points)
        param_score = min(10, metrics['parametrized_tests'] * 2)
        scores.append(param_score)
        
        # Edge cases (max 15 points)
        edge_score = min(15, metrics['edge_case_tests'])
        scores.append(edge_score)
        
        # Error handling (max 15 points)
        error_score = min(15, metrics['error_handling_tests'] * 2)
        scores.append(error_score)
        
        # Documentation (max 10 points)
        if metrics['total_test_functions'] > 0:
            doc_ratio = metrics['documented_tests'] / metrics['total_test_functions']
            doc_score = doc_ratio * 10
        else:
            doc_score = 0
        scores.append(doc_score)
        
        # Performance tests (max 10 points)
        perf_score = min(10, metrics['performance_tests'] * 2)
        scores.append(perf_score)
        
        return sum(scores)
    
    def print_report(self, report):
        """Print a formatted report."""
        print("\n" + "="*80)
        print("SciTeX Test Quality Report")
        print("="*80)
        
        print(f"\nSummary:")
        print(f"  Total modules analyzed: {report['summary']['total_modules']}")
        print(f"  Total test files: {report['summary']['total_test_files']}")
        print(f"  Total test functions: {report['summary']['total_test_functions']}")
        print(f"  Average quality score: {report['summary'].get('average_quality_score', 0):.1f}/100")
        
        if 'highest_quality_module' in report['summary']:
            module, score = report['summary']['highest_quality_module']
            print(f"  Highest quality: {module} ({score:.1f}/100)")
        
        if 'lowest_quality_module' in report['summary']:
            module, score = report['summary']['lowest_quality_module']
            print(f"  Lowest quality: {module} ({score:.1f}/100)")
        
        print(f"\nModules needing improvement (score < 50):")
        for module in report['needs_improvement']:
            score = report['quality_scores'][module]
            print(f"  - {module}: {score:.1f}/100")
        
        print(f"\nTop 10 modules by quality score:")
        sorted_modules = sorted(report['quality_scores'].items(), 
                              key=lambda x: x[1], reverse=True)[:10]
        for module, score in sorted_modules:
            metrics = report['module_details'][module]
            print(f"  {module}: {score:.1f}/100")
            print(f"    - Fixtures: {metrics['fixtures_defined']} defined, {metrics['fixtures_used']} used")
            print(f"    - Mocks: {metrics['mock_usage']} uses")
            print(f"    - Property tests: {metrics['property_tests']}")
            print(f"    - Edge cases: {metrics['edge_case_tests']}")
            print(f"    - Error handling: {metrics['error_handling_tests']}")
        
    def save_report(self, report, output_file="test_quality_report.json"):
        """Save report to JSON file."""
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\nDetailed report saved to: {output_file}")


def main():
    """Run test quality analysis."""
    analyzer = TestQualityAnalyzer()
    report = analyzer.analyze_all_tests()
    
    analyzer.print_report(report)
    analyzer.save_report(report)
    
    # Return exit code based on average quality
    avg_score = report['summary'].get('average_quality_score', 0)
    if avg_score < 40:
        return 1  # Fail if quality is too low
    return 0


if __name__ == "__main__":
    exit(main())

# EOF