#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-10 19:03:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/dev/test__analyze_code_flow_comprehensive.py

"""Comprehensive tests for code flow analysis functionality."""

import ast
import os
import tempfile
from textwrap import dedent
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest


class TestCodeFlowAnalyzerBasic:
    """Basic functionality tests for CodeFlowAnalyzer."""
    
    def test_import(self):
        """Test that CodeFlowAnalyzer and analyze_code_flow can be imported."""
        from scitex.dev import CodeFlowAnalyzer, analyze_code_flow
        assert callable(CodeFlowAnalyzer)
        assert callable(analyze_code_flow)
    
    def test_initialization(self):
        """Test CodeFlowAnalyzer initialization."""
        from scitex.dev import CodeFlowAnalyzer
        
        analyzer = CodeFlowAnalyzer("test.py")
        assert analyzer.file_path == "test.py"
        assert analyzer.execution_flow == []
        assert analyzer.sequence == 1
        assert isinstance(analyzer.skip_functions, set)
    
    def test_skip_functions_populated(self):
        """Test that skip_functions contains expected values."""
        from scitex.dev import CodeFlowAnalyzer
        
        analyzer = CodeFlowAnalyzer("test.py")
        
        # Check some expected skip functions
        assert "__init__" in analyzer.skip_functions
        assert "print" in analyzer.skip_functions
        assert "len" in analyzer.skip_functions
        assert "apply" in analyzer.skip_functions
        assert "reshape" in analyzer.skip_functions
    
    def test_analyze_simple_file(self):
        """Test analyzing a simple Python file."""
        from scitex.dev import CodeFlowAnalyzer
        
        code = dedent("""
        def hello():
            print("Hello")
        
        def main():
            hello()
        """)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            
            analyzer = CodeFlowAnalyzer(f.name)
            result = analyzer.analyze()
            
            assert "Execution Flow:" in result
            assert "hello" in result
            assert "main" in result
            
        os.unlink(f.name)


class TestCodeFlowAnalyzerTracing:
    """Test the tracing functionality."""
    
    def test_trace_function_definitions(self):
        """Test tracing function definitions."""
        from scitex.dev import CodeFlowAnalyzer
        
        code = dedent("""
        def func1():
            pass
        
        def func2():
            pass
        
        class MyClass:
            def method1(self):
                pass
        """)
        
        analyzer = CodeFlowAnalyzer(None)
        tree = ast.parse(code)
        analyzer._trace_calls(tree)
        
        # Check function names are captured
        flow_names = [call[1] for call in analyzer.execution_flow]
        assert "func1" in flow_names
        assert "func2" in flow_names
        assert "MyClass" in flow_names
        assert "method1" in flow_names
    
    def test_trace_function_calls(self):
        """Test tracing function calls."""
        from scitex.dev import CodeFlowAnalyzer
        
        code = dedent("""
        def helper():
            pass
        
        def main():
            helper()
            custom_func()
        """)
        
        analyzer = CodeFlowAnalyzer(None)
        tree = ast.parse(code)
        analyzer._trace_calls(tree)
        
        flow_names = [call[1] for call in analyzer.execution_flow]
        assert "helper" in flow_names
        assert "custom_func" in flow_names
    
    def test_trace_method_calls(self):
        """Test tracing method calls with attributes."""
        from scitex.dev import CodeFlowAnalyzer
        
        code = dedent("""
        def process():
            obj.method()
            module.submodule.function()
            self.internal_method()
        """)
        
        analyzer = CodeFlowAnalyzer(None)
        tree = ast.parse(code)
        analyzer._trace_calls(tree)
        
        flow_names = [call[1] for call in analyzer.execution_flow]
        assert "obj.method" in flow_names
        assert "module.submodule.function" in flow_names
        assert "self.internal_method" in flow_names
    
    def test_skip_builtin_functions(self):
        """Test that built-in functions are skipped."""
        from scitex.dev import CodeFlowAnalyzer
        
        code = dedent("""
        def process():
            print("hello")
            len([1, 2, 3])
            str(42)
            custom_function()
        """)
        
        analyzer = CodeFlowAnalyzer(None)
        tree = ast.parse(code)
        analyzer._trace_calls(tree)
        
        flow_names = [call[1] for call in analyzer.execution_flow]
        assert "print" not in flow_names
        assert "len" not in flow_names
        assert "str" not in flow_names
        assert "custom_function" in flow_names
    
    def test_depth_tracking(self):
        """Test that depth is tracked correctly."""
        from scitex.dev import CodeFlowAnalyzer
        
        code = dedent("""
        def outer():
            def inner():
                deep_function()
            inner()
        """)
        
        analyzer = CodeFlowAnalyzer(None)
        tree = ast.parse(code)
        analyzer._trace_calls(tree)
        
        # Check depths
        for depth, name, seq in analyzer.execution_flow:
            if name == "outer":
                assert depth >= 0
            elif name == "inner":
                assert depth > 0  # Should be deeper than outer
    
    def test_sequence_numbering(self):
        """Test that sequence numbers increment correctly."""
        from scitex.dev import CodeFlowAnalyzer
        
        code = dedent("""
        def func1():
            pass
        
        def func2():
            pass
        
        def func3():
            pass
        """)
        
        analyzer = CodeFlowAnalyzer(None)
        tree = ast.parse(code)
        analyzer._trace_calls(tree)
        
        sequences = [seq for _, _, seq in analyzer.execution_flow]
        # Sequences should be incrementing
        assert sequences == sorted(sequences)


class TestCodeFlowAnalyzerFormatting:
    """Test output formatting."""
    
    def test_format_output_structure(self):
        """Test the structure of formatted output."""
        from scitex.dev import CodeFlowAnalyzer
        
        analyzer = CodeFlowAnalyzer(None)
        analyzer.execution_flow = [
            (1, "main", 1),
            (2, "helper", 2),
            (3, "sub_helper", 3)
        ]
        
        output = analyzer._format_output()
        
        assert "Execution Flow:" in output
        assert "[01]" in output
        assert "main" in output
        assert "└──" in output  # Tree structure
    
    def test_format_indentation(self):
        """Test proper indentation based on depth."""
        from scitex.dev import CodeFlowAnalyzer
        
        analyzer = CodeFlowAnalyzer(None)
        analyzer.execution_flow = [
            (1, "level1", 1),
            (2, "level2", 2),
            (3, "level3", 3)
        ]
        
        output = analyzer._format_output()
        lines = output.split('\n')
        
        # Check indentation increases with depth
        for line in lines[1:]:  # Skip header
            if "level2" in line:
                assert line.startswith("    ")  # More spaces than level1
            elif "level3" in line:
                assert line.startswith("        ")  # Even more spaces
    
    def test_skip_private_methods(self):
        """Test that private methods are filtered out."""
        from scitex.dev import CodeFlowAnalyzer
        
        analyzer = CodeFlowAnalyzer(None)
        analyzer.execution_flow = [
            (1, "public_func", 1),
            (2, "_private_func", 2),
            (3, "nested_in_private", 3),
            (2, "public_after_private", 4)
        ]
        
        output = analyzer._format_output()
        
        assert "public_func" in output
        assert "_private_func" not in output
        assert "nested_in_private" not in output
        assert "public_after_private" in output


class TestCodeFlowAnalyzerErrorHandling:
    """Test error handling."""
    
    def test_nonexistent_file(self):
        """Test handling of non-existent file."""
        from scitex.dev import CodeFlowAnalyzer
        
        analyzer = CodeFlowAnalyzer("/nonexistent/file.py")
        result = analyzer.analyze()
        
        # Should return error message, not crash
        assert isinstance(result, str)
    
    def test_invalid_python_syntax(self):
        """Test handling of invalid Python syntax."""
        from scitex.dev import CodeFlowAnalyzer
        
        code = "def invalid syntax here:"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            
            analyzer = CodeFlowAnalyzer(f.name)
            result = analyzer.analyze()
            
            # Should handle syntax error gracefully
            assert isinstance(result, str)
            
        os.unlink(f.name)
    
    def test_empty_file(self):
        """Test analyzing empty file."""
        from scitex.dev import CodeFlowAnalyzer
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("")
            f.flush()
            
            analyzer = CodeFlowAnalyzer(f.name)
            result = analyzer.analyze()
            
            assert "Execution Flow:" in result
            
        os.unlink(f.name)
    
    @patch('builtins.open', side_effect=PermissionError("Access denied"))
    def test_permission_error(self, mock_file):
        """Test handling of permission errors."""
        from scitex.dev import CodeFlowAnalyzer
        
        analyzer = CodeFlowAnalyzer("protected.py")
        result = analyzer.analyze()
        
        # Should return error message
        assert isinstance(result, str)
        assert "Access denied" in result or "PermissionError" in result


class TestAnalyzeCodeFlowFunction:
    """Test the analyze_code_flow convenience function."""
    
    def test_analyze_code_flow_wrapper(self):
        """Test analyze_code_flow wrapper function."""
        from scitex.dev import analyze_code_flow
        
        code = dedent("""
        def test_function():
            pass
        """)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            
            result = analyze_code_flow(f.name)
            
            assert "Execution Flow:" in result
            assert "test_function" in result
            
        os.unlink(f.name)
    
    @patch('scitex.dev._analyze_code_flow.CodeFlowAnalyzer')
    def test_analyze_code_flow_creates_analyzer(self, mock_analyzer_class):
        """Test that analyze_code_flow creates CodeFlowAnalyzer instance."""
        from scitex.dev import analyze_code_flow
        
        mock_instance = MagicMock()
        mock_instance.analyze.return_value = "Test result"
        mock_analyzer_class.return_value = mock_instance
        
        result = analyze_code_flow("test.py")
        
        mock_analyzer_class.assert_called_once_with("test.py")
        mock_instance.analyze.assert_called_once()
        assert result == "Test result"


class TestCodeFlowAnalyzerMainGuard:
    """Test handling of if __name__ == "__main__" blocks."""
    
    def test_truncate_at_main_guard(self):
        """Test that code after main guard is ignored."""
        from scitex.dev import CodeFlowAnalyzer
        
        code = dedent("""
        def before_main():
            pass
        
        if __name__ == "__main__":
            def after_main():
                pass
            after_main()
        """)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            
            analyzer = CodeFlowAnalyzer(f.name)
            result = analyzer.analyze()
            
            assert "before_main" in result
            assert "after_main" not in result
            
        os.unlink(f.name)
    
    def test_no_main_guard(self):
        """Test files without main guard."""
        from scitex.dev import CodeFlowAnalyzer
        
        code = dedent("""
        def func1():
            pass
        
        def func2():
            pass
        
        func1()
        func2()
        """)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            
            analyzer = CodeFlowAnalyzer(f.name)
            result = analyzer.analyze()
            
            assert "func1" in result
            assert "func2" in result
            
        os.unlink(f.name)


class TestCodeFlowAnalyzerComplexCases:
    """Test complex code structures."""
    
    def test_nested_classes_and_methods(self):
        """Test nested classes and methods."""
        from scitex.dev import CodeFlowAnalyzer
        
        code = dedent("""
        class OuterClass:
            def outer_method(self):
                class InnerClass:
                    def inner_method(self):
                        deep_function()
        """)
        
        analyzer = CodeFlowAnalyzer(None)
        tree = ast.parse(code)
        analyzer._trace_calls(tree)
        
        flow_names = [call[1] for call in analyzer.execution_flow]
        assert "OuterClass" in flow_names
        assert "outer_method" in flow_names
        assert "InnerClass" in flow_names
        assert "inner_method" in flow_names
        assert "deep_function" in flow_names
    
    def test_decorators(self):
        """Test handling of decorated functions."""
        from scitex.dev import CodeFlowAnalyzer
        
        code = dedent("""
        @decorator1
        @decorator2
        def decorated_func():
            pass
        
        @property
        def prop_method(self):
            return self.value
        """)
        
        analyzer = CodeFlowAnalyzer(None)
        tree = ast.parse(code)
        analyzer._trace_calls(tree)
        
        flow_names = [call[1] for call in analyzer.execution_flow]
        assert "decorated_func" in flow_names
        assert "prop_method" in flow_names
    
    def test_lambda_functions(self):
        """Test handling of lambda functions."""
        from scitex.dev import CodeFlowAnalyzer
        
        code = dedent("""
        def use_lambda():
            result = map(lambda x: x * 2, [1, 2, 3])
            custom_lambda = lambda y: process(y)
        """)
        
        analyzer = CodeFlowAnalyzer(None)
        tree = ast.parse(code)
        analyzer._trace_calls(tree)
        
        flow_names = [call[1] for call in analyzer.execution_flow]
        assert "use_lambda" in flow_names
        assert "process" in flow_names  # Should find call inside lambda
    
    def test_comprehensions(self):
        """Test handling of comprehensions."""
        from scitex.dev import CodeFlowAnalyzer
        
        code = dedent("""
        def use_comprehensions():
            result1 = [process(x) for x in items]
            result2 = {transform(k): v for k, v in data.items()}
            result3 = (compute(i) for i in range(10))
        """)
        
        analyzer = CodeFlowAnalyzer(None)
        tree = ast.parse(code)
        analyzer._trace_calls(tree)
        
        flow_names = [call[1] for call in analyzer.execution_flow]
        assert "process" in flow_names
        assert "transform" in flow_names
        assert "compute" in flow_names


class TestGetFuncName:
    """Test the _get_func_name helper method."""
    
    def test_get_func_name_simple(self):
        """Test getting simple function names."""
        from scitex.dev import CodeFlowAnalyzer
        
        code = "func()"
        tree = ast.parse(code)
        call_node = tree.body[0].value
        
        analyzer = CodeFlowAnalyzer(None)
        name = analyzer._get_func_name(call_node)
        
        assert name == "func"
    
    def test_get_func_name_attribute(self):
        """Test getting attribute function names."""
        from scitex.dev import CodeFlowAnalyzer
        
        code = "obj.method()"
        tree = ast.parse(code)
        call_node = tree.body[0].value
        
        analyzer = CodeFlowAnalyzer(None)
        name = analyzer._get_func_name(call_node)
        
        assert name == "obj.method"
    
    def test_get_func_name_nested_attribute(self):
        """Test getting nested attribute names."""
        from scitex.dev import CodeFlowAnalyzer
        
        code = "module.submodule.function()"
        tree = ast.parse(code)
        call_node = tree.body[0].value
        
        analyzer = CodeFlowAnalyzer(None)
        name = analyzer._get_func_name(call_node)
        
        assert name == "module.submodule.function"
    
    def test_get_func_name_skip_function(self):
        """Test that skip functions return None."""
        from scitex.dev import CodeFlowAnalyzer
        
        code = "print('hello')"
        tree = ast.parse(code)
        call_node = tree.body[0].value
        
        analyzer = CodeFlowAnalyzer(None)
        name = analyzer._get_func_name(call_node)
        
        assert name is None  # print is in skip_functions


class TestCodeFlowAnalyzerRealWorld:
    """Test with real-world code patterns."""
    
    def test_django_view(self):
        """Test analyzing Django-style view."""
        from scitex.dev import CodeFlowAnalyzer
        
        code = dedent("""
        from django.shortcuts import render
        
        def index(request):
            context = get_context()
            return render(request, 'index.html', context)
        
        def get_context():
            data = fetch_data()
            return process_data(data)
        """)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            
            analyzer = CodeFlowAnalyzer(f.name)
            result = analyzer.analyze()
            
            assert "index" in result
            assert "get_context" in result
            assert "fetch_data" in result
            assert "process_data" in result
            
        os.unlink(f.name)
    
    def test_data_science_workflow(self):
        """Test analyzing data science workflow."""
        from scitex.dev import CodeFlowAnalyzer
        
        code = dedent("""
        import pandas as pd
        import numpy as np
        
        def load_data():
            df = pd.read_csv('data.csv')
            return preprocess(df)
        
        def preprocess(df):
            df = clean_data(df)
            df = transform_features(df)
            return df
        
        def train_model(df):
            X, y = prepare_features(df)
            model = create_model()
            model.fit(X, y)
            return model
        """)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            
            analyzer = CodeFlowAnalyzer(f.name)
            result = analyzer.analyze()
            
            # Should track custom functions but not pandas methods
            assert "load_data" in result
            assert "preprocess" in result
            assert "clean_data" in result
            assert "train_model" in result
            assert "read_csv" not in result  # Skipped
            assert "fit" not in result  # Skipped
            
        os.unlink(f.name)


class TestCodeFlowAnalyzerPerformance:
    """Test performance with large files."""
    
    def test_large_file_performance(self):
        """Test analyzing large file completes in reasonable time."""
        from scitex.dev import CodeFlowAnalyzer
        import time
        
        # Generate large code file
        code_parts = ["def func0(): pass"]
        for i in range(1, 1000):
            code_parts.append(f"def func{i}():\n    func{i-1}()")
        
        code = "\n".join(code_parts)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            
            analyzer = CodeFlowAnalyzer(f.name)
            
            start_time = time.time()
            result = analyzer.analyze()
            duration = time.time() - start_time
            
            assert duration < 5.0  # Should complete within 5 seconds
            assert "Execution Flow:" in result
            
        os.unlink(f.name)


class TestCodeFlowAnalyzerIntegration:
    """Integration tests with main function."""
    
    @patch('scitex.dev._analyze_code_flow.__file__', '/test/file.py')
    @patch('builtins.print')
    def test_main_function(self, mock_print):
        """Test main function execution."""
        from scitex.dev import main
        
        # Create mock args
        args = MagicMock()
        
        with patch('scitex.dev._analyze_code_flow.analyze_code_flow') as mock_analyze:
            mock_analyze.return_value = "Test flow output"
            
            result = main(args)
            
            assert result == 0
            mock_print.assert_called_with("Test flow output")
    
    def test_parse_args(self):
        """Test argument parsing."""
        from scitex.dev import parse_args
        
        with patch('sys.argv', ['script.py', '--var', '5', '--flag']):
            with patch('scitex.str.printc'):  # Mock the print function
                args = parse_args()
                
                assert args.var == 5
                assert args.flag is True


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v"])