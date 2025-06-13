#!/usr/bin/env python3
"""Generate API documentation files for MNGS modules."""

from pathlib import Path

# API documentation template
API_TEMPLATE = """{module_name} API Reference
{underline}

.. automodule:: {module_path}
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

Submodules
----------

.. autosummary::
   :toctree: generated
   :recursive:

   {module_path}
"""

def create_api_doc(module_name, module_path, output_file):
    """Create an API documentation file for a module."""
    title = f"mngs.{module_name}"
    underline = "=" * len(title + " API Reference")
    
    content = API_TEMPLATE.format(
        module_name=title,
        module_path=module_path,
        underline=underline
    )
    
    with open(output_file, 'w') as f:
        f.write(content)
    print(f"Created: {output_file}")

def main():
    # Create API directory
    api_dir = Path(__file__).parent / "api"
    api_dir.mkdir(exist_ok=True)
    
    # Define modules
    modules = [
        ("gen", "mngs.gen"),
        ("io", "mngs.io"),
        ("plt", "mngs.plt"),
        ("dsp", "mngs.dsp"),
        ("stats", "mngs.stats"),
        ("pd", "mngs.pd"),
        ("ai", "mngs.ai"),
        ("nn", "mngs.nn"),
        ("db", "mngs.db"),
        ("decorators", "mngs.decorators"),
        ("path", "mngs.path"),
        ("str", "mngs.str"),
        ("dict", "mngs.dict"),
    ]
    
    # Create API documentation files
    for module_name, module_path in modules:
        output_file = api_dir / f"mngs.{module_name}.rst"
        create_api_doc(module_name, module_path, output_file)

if __name__ == "__main__":
    main()