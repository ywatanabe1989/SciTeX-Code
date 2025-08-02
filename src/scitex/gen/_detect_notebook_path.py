#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-04 11:22:00 (ywatanabe)"
# File: ./src/scitex/gen/_detect_notebook_path.py

"""
Detect Jupyter notebook filename for consistent output paths.

When running in a notebook like ./examples/analysis.ipynb,
outputs should go to ./examples/analysis_out/
"""

import os
import json
from typing import Optional

__all__ = ['get_notebook_path', 'get_notebook_output_dir']


def get_notebook_path() -> Optional[str]:
    """
    Get the path of the currently running Jupyter notebook.
    
    Returns
    -------
    Optional[str]
        Path to the notebook file, or None if not in a notebook
        
    Examples
    --------
    >>> path = get_notebook_path()
    >>> print(path)
    ./examples/my_analysis.ipynb
    """
    try:
        # Method 1: Try to get from IPython
        ip = get_ipython()
        
        # Check if we're in a notebook
        if not (ip and type(ip).__name__ == 'ZMQInteractiveShell'):
            return None
            
        # Method 2: Check IPython's notebook_name
        if hasattr(ip, 'notebook_name'):
            return ip.notebook_name
            
        # Method 3: Try to get from kernel connection file
        import re
        import glob
        
        # Get kernel ID from the current session
        kernel_id = re.search(
            r'kernel-(.*?)\.json',
            ip.config['IPKernelApp']['connection_file']
        ).group(1)
        
        # Search for notebook sessions
        runtime_dir = os.environ.get('JUPYTER_RUNTIME_DIR', 
                                     os.path.expanduser('~/.local/share/jupyter/runtime'))
        
        for nbserver in glob.glob(os.path.join(runtime_dir, 'nbserver-*.json')):
            try:
                with open(nbserver, 'r') as f:
                    server_info = json.load(f)
                    
                # Check notebook sessions
                import requests
                sessions_url = f"{server_info['url']}api/sessions?token={server_info.get('token', '')}"
                response = requests.get(sessions_url)
                
                if response.status_code == 200:
                    sessions = response.json()
                    for session in sessions:
                        if session['kernel']['id'] == kernel_id:
                            # Found our notebook!
                            notebook_path = session['notebook']['path']
                            return notebook_path
            except:
                continue
                
        # Method 4: Try JavaScript bridge (if available)
        try:
            from IPython.display import Javascript, display
            import time
            
            # This won't work in papermill, but works in interactive notebooks
            display(Javascript('''
                IPython.notebook.kernel.execute(
                    `__notebook_path__ = '${IPython.notebook.notebook_path}'`
                );
            '''))
            
            # Brief pause for JS execution
            time.sleep(0.1)
            
            if '__notebook_path__' in globals():
                return globals()['__notebook_path__']
        except:
            pass
            
    except Exception:
        pass
        
    return None


def get_notebook_output_dir(notebook_path: Optional[str] = None) -> Optional[str]:
    """
    Get the output directory for a notebook.
    
    Parameters
    ----------
    notebook_path : Optional[str]
        Path to notebook, or None to auto-detect
        
    Returns
    -------
    Optional[str]
        Output directory path like ./examples/analysis_out/
        
    Examples
    --------
    >>> output_dir = get_notebook_output_dir()
    >>> print(output_dir)
    ./examples/analysis_out/
    
    >>> output_dir = get_notebook_output_dir('./docs/tutorial.ipynb')
    >>> print(output_dir)
    ./docs/tutorial_out/
    """
    if notebook_path is None:
        notebook_path = get_notebook_path()
        
    if not notebook_path:
        return None
        
    # Get directory and base name
    notebook_dir = os.path.dirname(notebook_path) or '.'
    notebook_base = os.path.splitext(os.path.basename(notebook_path))[0]
    
    # Create output directory path
    output_dir = os.path.join(notebook_dir, f"{notebook_base}_out")
    
    return output_dir


def detect_notebook_from_cwd() -> Optional[str]:
    """
    Fallback: Try to detect notebook from current working directory.
    
    If there's exactly one .ipynb file in the current directory,
    assume that's the running notebook.
    
    Returns
    -------
    Optional[str]
        Path to notebook or None
    """
    import glob
    
    notebooks = glob.glob('*.ipynb')
    
    # Only use this method if there's exactly one notebook
    if len(notebooks) == 1:
        return notebooks[0]
        
    return None

# EOF