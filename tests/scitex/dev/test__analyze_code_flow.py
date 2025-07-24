# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/dev/_analyze_code_flow.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-20 10:27:28 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/dev/_analyze_code_flow.py
# 
# THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/dev/_analyze_code_flow.py"
# 
# import ast
# 
# import matplotlib.pyplot as plt
# import scitex
# 
# 
# class CodeFlowAnalyzer:
#     def __init__(self, file_path: str):
#         self.file_path = file_path
#         self.execution_flow = []
#         self.sequence = 1
#         self.skip_functions = {
#             "__init__",
#             "__main__",
#             # Python built-ins
#             "len",
#             "min",
#             "max",
#             "sum",
#             "enumerate",
#             "eval",
#             "print",
#             "str",
#             "int",
#             "float",
#             "list",
#             "dict",
#             "set",
#             "tuple",
#             "any",
#             "all",
#             "map",
#             "filter",
#             "zip",
#             # Common DataFrame operations
#             "apply",
#             "unique",
#             "tolist",
#             "to_list",
#             "rename",
#             "merge",
#             "set_index",
#             "reset_index",
#             "groupby",
#             "sort_values",
#             "iloc",
#             "loc",
#             "where",
#             # NumPy operations
#             "reshape",
#             "squeeze",
#             "stack",
#             "concatenate",
#             "array",
#             "zeros",
#             "ones",
#             "full",
#             "empty",
#             "frombuffer",
#             # Common attributes/methods
#             "shape",
#             "dtype",
#             "size",
#             "index",
#             "columns",
#             "values",
#             "name",
#             "names",
#             # File operations
#             "open",
#             "read",
#             "write",
#             "close",
#             # String operations
#             "join",
#             "split",
#             "strip",
#             "replace",
#             # Custom
#             "scitex.str.printc",
#             "printc",
#             "scitex.io.load_configs",
#             "parse_args",
#             "run_main",
#             "load_configs",
#         }
#         # self.seen_calls = set()  # Track unique function calls
# 
#     def _trace_calls(self, node, depth=0):
#         sequence_orig = self.sequence
# 
#         if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
# 
#             if node.name not in self.skip_functions:
#                 # Track all function definitions
#                 self.execution_flow.append((depth, node.name, self.sequence))
#                 self.sequence += 1
# 
#         if isinstance(node, ast.Call):
#             if isinstance(node.func, ast.Name):
#                 func_name = node.func.id
# 
#                 if func_name not in self.skip_functions:
#                     self.execution_flow.append((depth, func_name, self.sequence))
#                     self.sequence += 1
# 
#             elif isinstance(node.func, ast.Attribute):
#                 parts = []
#                 current = node.func
#                 while isinstance(current, ast.Attribute):
#                     parts.insert(0, current.attr)
#                     current = current.value
#                 if isinstance(current, ast.Name):
#                     parts.insert(0, current.id)
#                 func_name = ".".join(parts)
# 
#                 if not any(skip in func_name for skip in self.skip_functions):
#                     self.execution_flow.append((depth, func_name, self.sequence))
#                     self.sequence += 1
# 
#         if self.sequence == 1:
#             depth = 0
# 
#         for child in ast.iter_child_nodes(node):
#             self._trace_calls(child, depth + 1)
# 
#     def _get_func_name(self, node):
#         if isinstance(node.func, ast.Name):
#             return node.func.id
#         elif isinstance(node.func, ast.Attribute):
#             parts = []
#             current = node.func
#             while isinstance(current, ast.Attribute):
#                 parts.insert(0, current.attr)
#                 current = current.value
#             if isinstance(current, ast.Name):
#                 parts.insert(0, current.id)
#             func_name = ".".join(parts)
#             return (
#                 func_name
#                 if not any(skip in func_name for skip in self.skip_functions)
#                 else None
#             )
#         return None
# 
#     def _format_output(self):
#         output = ["Execution Flow:"]
#         last_depth = 1
#         skip_until_depth = None
# 
#         filtered_flow = []
# 
#         for depth, call, seq in self.execution_flow:
# 
#             # Start skipping when encountering private method
#             if call.startswith(("_", "self._")):
#                 skip_until_depth = depth
#                 continue
# 
#             # Skip all nested calls within private methods
#             if skip_until_depth is not None and depth > skip_until_depth:
#                 continue
#             else:
#                 skip_until_depth = None
# 
#             filtered_flow.append((depth, call, seq))
#             last_depth = depth
# 
#         # Reset seq on depth == 1
#         seq_prev = 0
#         for ii, flow in enumerate(filtered_flow):
#             depth, call, seq = flow
#             if depth == 1:
#                 seq_current = 1
#                 seq_prev = 1
#             else:
#                 if depth > 1:
#                     seq_current = seq_prev + 1
#                     seq_prev = seq_current
#                 else:
#                     seq_current = 0
#                     seq_prev = 0
# 
#             filtered_flow[ii] = (depth, call, seq_current)
# 
#         for depth, call, seq in filtered_flow:
#             prefix = "    " * depth
#             if depth == 1:
#                 line = f"\n{prefix}[{int(seq) if isinstance(seq, float) else seq:02d}] {call}"
#             else:
#                 line = f"{prefix}[{int(seq) if isinstance(seq, float) else seq:02d}] └── {call}"
#             output.append(line)
# 
#         return "\n".join(output)
# 
#     def analyze(self):
#         if self.file_path:
#             try:
#                 with open(self.file_path, "r") as file:
#                     content = file.read()
# 
#                     # Find main guard position and truncate content
#                     if "if __name__" in content:
#                         main_guard_pos = content.find("if __name__")
#                         content = content[:main_guard_pos].strip()
# 
#                     tree = ast.parse(content)
#                 self._trace_calls(tree)
#                 return self._format_output()
#             except Exception as e:
#                 print(e)
#                 return str(e)
# 
# 
# def analyze_code_flow(lpath):
#     return CodeFlowAnalyzer(lpath).analyze()
# 
# 
# def main(args):
#     diagram = analyze_code_flow(__file__)
#     print(diagram)
#     return 0
# 
# 
# def parse_args():
#     import argparse
# 
#     import scitex
# 
#     is_script = scitex.gen.is_script()
# 
#     parser = argparse.ArgumentParser(description="")
#     parser.add_argument(
#         "--var",
#         "-v",
#         type=int,
#         choices=None,
#         default=1,
#         help="(default: %%(default)s)",
#     )
#     parser.add_argument(
#         "--flag",
#         "-f",
#         action="store_true",
#         default=False,
#         help="(default: %%(default)s)",
#     )
#     args = parser.parse_args()
#     scitex.str.printc(args, c="yellow")
# 
#     return args
# 
# 
# if __name__ == "__main__":
#     import sys
# 
#     import matplotlib.pyplot as plt
# 
#     CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(
#         sys,
#         plt,
#         verbose=False,
#         agg=True,
#     )
# 
#     exit_status = main(parse_args())
# 
#     scitex.gen.close(
#         CONFIG,
#         verbose=False,
#         notify=False,
#         message="",
#         exit_status=exit_status,
#     )
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/dev/_analyze_code_flow.py
# --------------------------------------------------------------------------------
