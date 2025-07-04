#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-02 02:55:00 (ywatanabe)"
# File: ./mcp_servers/scitex_io_translator/translators/template_translator.py
# ----------------------------------------
import os
__FILE__ = "./mcp_servers/scitex_io_translator/translators/template_translator.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
"""Template translator for adding/removing SciTeX boilerplate."""

import re
from datetime import datetime
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class TemplateTranslator:
    """Handles SciTeX template and boilerplate code."""
    
    def __init__(self):
        self.author = "ywatanabe"  # Default author
        
    def add_boilerplate(self, code: str, preserve_comments: bool = True) -> str:
        """Add SciTeX boilerplate to standard Python code."""
        
        # Extract shebang and encoding if present
        shebang, encoding, clean_code = self._extract_header(code)
        
        # Detect script name from imports or context
        script_name = self._detect_script_name(clean_code)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Build the header
        header_lines = []
        
        # Shebang
        if shebang:
            header_lines.append(shebang)
        else:
            header_lines.append("#!/usr/bin/env python3")
        
        # Encoding
        if encoding:
            header_lines.append(encoding)
        else:
            header_lines.append("# -*- coding: utf-8 -*-")
        
        # Timestamp and file info
        header_lines.extend([
            f'# Timestamp: "{timestamp} ({self.author})"',
            f'# File: {script_name}',
            '# ----------------------------------------',
            'import os',
            f'__FILE__ = "{script_name}"',
            '__DIR__ = os.path.dirname(__FILE__)',
            '# ----------------------------------------',
            ''
        ])
        
        # Extract imports and separate from main code
        imports, main_code = self._separate_imports(clean_code)
        
        # Add main function wrapper if needed
        if self._needs_main_wrapper(main_code):
            main_code = self._wrap_in_main(main_code)
        
        # Add run_main boilerplate if needed
        if 'def main(' in main_code:
            main_code = self._add_run_main_boilerplate(main_code)
        
        # Combine all parts
        result = '\n'.join(header_lines)
        if imports:
            result += '\n' + imports + '\n'
        result += '\n' + main_code
        
        return result
    
    def remove_boilerplate(self, code: str) -> str:
        """Remove SciTeX boilerplate from code."""
        lines = code.split('\n')
        result_lines = []
        
        # Skip header section
        skip_until = 0
        for i, line in enumerate(lines):
            if '# ----------------------------------------' in line:
                skip_until = i + 1
                if i + 1 < len(lines) and lines[i + 1].strip() == '':
                    skip_until = i + 2
                break
        
        # Remove __FILE__ and __DIR__ definitions
        in_header = True
        for i in range(skip_until, len(lines)):
            line = lines[i]
            
            if in_header:
                if line.startswith('import os') and '__FILE__' in '\n'.join(lines[i:i+3]):
                    continue
                elif line.startswith('__FILE__') or line.startswith('__DIR__'):
                    continue
                elif line.strip() == '' and i + 1 < len(lines) and not lines[i + 1].strip().startswith('__'):
                    in_header = False
                    continue
            
            # Remove run_main boilerplate
            if 'def run_main(' in line:
                # Skip the entire run_main function
                brace_count = 1
                i += 1
                while i < len(lines) and brace_count > 0:
                    if lines[i].strip().startswith('def '):
                        break
                    i += 1
                continue
            
            # Simplify if __name__ == "__main__" section
            if line.strip() == 'if __name__ == "__main__":':
                if i + 1 < len(lines) and 'run_main()' in lines[i + 1]:
                    result_lines.append(line)
                    result_lines.append('    main()')
                    i += 1
                    continue
            
            result_lines.append(line)
        
        # Clean up extra blank lines
        cleaned = []
        prev_blank = False
        for line in result_lines:
            if line.strip() == '':
                if not prev_blank:
                    cleaned.append(line)
                prev_blank = True
            else:
                cleaned.append(line)
                prev_blank = False
        
        return '\n'.join(cleaned)
    
    def _extract_header(self, code: str) -> Tuple[Optional[str], Optional[str], str]:
        """Extract shebang and encoding from code."""
        lines = code.split('\n')
        shebang = None
        encoding = None
        start_idx = 0
        
        # Check for shebang
        if lines and lines[0].startswith('#!'):
            shebang = lines[0]
            start_idx = 1
        
        # Check for encoding
        if start_idx < len(lines) and 'coding' in lines[start_idx]:
            encoding = lines[start_idx]
            start_idx += 1
        
        clean_code = '\n'.join(lines[start_idx:])
        return shebang, encoding, clean_code
    
    def _detect_script_name(self, code: str) -> str:
        """Try to detect script name from code."""
        # Look for __file__ references
        file_match = re.search(r'__file__\s*=\s*["\'](.+?)["\']', code)
        if file_match:
            return file_match.group(1)
        
        # Look for main module docstring
        doc_match = re.search(r'"""(.+?)\.py', code)
        if doc_match:
            return f"./{doc_match.group(1)}.py"
        
        # Default
        return "./script.py"
    
    def _separate_imports(self, code: str) -> Tuple[str, str]:
        """Separate imports from main code."""
        lines = code.split('\n')
        import_lines = []
        main_lines = []
        
        in_imports = True
        for line in lines:
            if in_imports:
                if (line.strip().startswith('import ') or 
                    line.strip().startswith('from ') or
                    line.strip() == '' or
                    line.strip().startswith('#')):
                    import_lines.append(line)
                else:
                    in_imports = False
                    main_lines.append(line)
            else:
                main_lines.append(line)
        
        return '\n'.join(import_lines).strip(), '\n'.join(main_lines).strip()
    
    def _needs_main_wrapper(self, code: str) -> bool:
        """Check if code needs to be wrapped in main function."""
        # Don't wrap if already has main
        if 'def main(' in code:
            return False
        
        # Check for top-level executable code
        lines = code.split('\n')
        for line in lines:
            stripped = line.strip()
            if (stripped and 
                not stripped.startswith('#') and
                not stripped.startswith('def ') and
                not stripped.startswith('class ') and
                not stripped.startswith('@') and
                not stripped.startswith('import ') and
                not stripped.startswith('from ')):
                return True
        
        return False
    
    def _wrap_in_main(self, code: str) -> str:
        """Wrap code in main function."""
        lines = code.split('\n')
        
        # Find where executable code starts
        function_lines = []
        main_lines = []
        in_main = False
        
        for line in lines:
            if (not in_main and 
                line.strip() and 
                not line.strip().startswith('#') and
                not line.strip().startswith('def ') and
                not line.strip().startswith('class ') and
                not line.strip().startswith('@')):
                in_main = True
            
            if in_main:
                main_lines.append('    ' + line if line.strip() else line)
            else:
                function_lines.append(line)
        
        # Build result
        result = '\n'.join(function_lines)
        if function_lines and function_lines[-1].strip():
            result += '\n\n'
        
        result += 'def main():\n'
        result += '    """Main function."""\n'
        result += '\n'.join(main_lines)
        result += '\n    return 0\n'
        
        return result
    
    def _add_run_main_boilerplate(self, code: str) -> str:
        """Add run_main boilerplate for proper SciTeX execution."""
        
        # Check if already has if __name__ == "__main__"
        if 'if __name__ == "__main__"' in code:
            return code
        
        run_main_template = '''

def run_main():
    """Run main function with proper setup."""
    import sys
    CONFIG, sys.stdout, sys.stderr, plt, CC = stx.gen.start(
        sys, plt, verbose=True
    )
    main(CONFIG)
    stx.gen.close(CONFIG, verbose=True)


if __name__ == "__main__":
    run_main()'''
        
        return code + run_main_template