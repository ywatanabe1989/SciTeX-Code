#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-04 11:17:00 (ywatanabe)"
# File: ./src/scitex/plt/utils/_scientific_captions.py

"""
Functionality:
    Scientific figure caption system for publication-ready figures
Input:
    Figure objects, caption text, and formatting parameters
Output:
    Figures with properly formatted scientific captions
Prerequisites:
    matplotlib, textwrap
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import textwrap
from typing import Union, List, Dict, Tuple, Optional
import re


class ScientificCaption:
    """
    A comprehensive caption system for scientific figures with support for:
    - Figure-level captions
    - Panel-level captions (A, B, C, etc.)
    - Automatic numbering
    - Cross-references
    - Multiple formatting styles
    """
    
    def __init__(self):
        self.figure_counter = 0
        self.caption_registry = {}
        self.panel_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
    
    def add_figure_caption(
        self,
        fig,
        caption: str,
        figure_label: str = None,
        style: str = "scientific",
        position: str = "bottom",
        width_ratio: float = 0.9,
        font_size: Union[str, int] = "small",
        wrap_width: int = 80,
        save_to_file: bool = False,
        file_path: str = None
    ) -> str:
        """
        Add a scientific caption to a figure.
        
        Parameters
        ----------
        fig : matplotlib.figure.Figure
            The figure to add caption to
        caption : str
            The caption text
        figure_label : str, optional
            Custom figure label (e.g., "Figure 1"), auto-generated if None
        style : str, optional
            Caption style: "scientific", "nature", "ieee", "apa", by default "scientific"
        position : str, optional
            Caption position: "bottom", "top", by default "bottom"
        width_ratio : float, optional
            Width of caption relative to figure width, by default 0.9
        font_size : Union[str, int], optional
            Font size for caption, by default "small"
        wrap_width : int, optional
            Character width for text wrapping, by default 80
        save_to_file : bool, optional
            Whether to save caption to separate file, by default False
        file_path : str, optional
            Path for caption file, by default None
            
        Returns
        -------
        str
            The formatted caption text
        """
        # Generate figure label if not provided
        if figure_label is None:
            self.figure_counter += 1
            figure_label = f"Figure {self.figure_counter}"
        
        # Format caption according to style
        formatted_caption = self._format_caption(caption, figure_label, style, wrap_width)
        
        # Add caption to figure
        self._add_caption_to_figure(fig, formatted_caption, position, width_ratio, font_size)
        
        # Register caption
        self.caption_registry[figure_label] = {
            'text': caption,
            'formatted': formatted_caption,
            'style': style,
            'figure': fig
        }
        
        # Save to file if requested
        if save_to_file:
            self._save_caption_to_file(formatted_caption, figure_label, file_path)
        
        return formatted_caption
    
    def add_panel_captions(
        self,
        fig,
        axes,
        panel_captions: Union[List[str], Dict[str, str]],
        main_caption: str = "",
        figure_label: str = None,
        panel_style: str = "letter_bold",
        position: str = "top_left",
        font_size: Union[str, int] = "medium",
        offset: Tuple[float, float] = (0.02, 0.98)
    ) -> Dict[str, str]:
        """
        Add panel captions (A, B, C, etc.) to subplot panels.
        
        Parameters
        ----------
        fig : matplotlib.figure.Figure
            The figure containing panels
        axes : Union[matplotlib.axes.Axes, List, np.ndarray]
            Axes objects for each panel
        panel_captions : Union[List[str], Dict[str, str]]
            Caption text for each panel, either list or dict with panel labels
        main_caption : str, optional
            Main figure caption, by default ""
        figure_label : str, optional
            Figure label, by default None
        panel_style : str, optional
            Panel label style: "letter_bold", "letter_italic", "number", by default "letter_bold"
        position : str, optional
            Panel label position: "top_left", "top_right", "bottom_left", "bottom_right", by default "top_left"
        font_size : Union[str, int], optional
            Font size for panel labels, by default "medium"
        offset : Tuple[float, float], optional
            Position offset for panel labels, by default (0.02, 0.98)
            
        Returns
        -------
        Dict[str, str]
            Dictionary mapping panel labels to full caption text
        """
        # Ensure axes is a list
        if not isinstance(axes, (list, tuple)):
            axes = [axes] if hasattr(axes, 'plot') else axes.flatten()
        
        # Handle different input formats for panel_captions
        if isinstance(panel_captions, list):
            panel_dict = {self.panel_letters[i]: panel_captions[i] 
                         for i in range(min(len(panel_captions), len(axes)))}
        else:
            panel_dict = panel_captions
        
        # Add panel labels to axes
        formatted_panels = {}
        for i, ax in enumerate(axes):
            if i < len(self.panel_letters):
                panel_letter = self.panel_letters[i]
                if panel_letter in panel_dict:
                    formatted_label = self._format_panel_label(panel_letter, panel_style)
                    panel_caption = panel_dict[panel_letter]
                    
                    # Add label to axes
                    self._add_panel_label_to_axes(ax, formatted_label, position, font_size, offset)
                    
                    formatted_panels[panel_letter] = f"{formatted_label} {panel_caption}"
        
        # Add main caption if provided
        if main_caption:
            full_caption = self._combine_panel_and_main_captions(formatted_panels, main_caption)
            self.add_figure_caption(fig, full_caption, figure_label)
        
        return formatted_panels
    
    def _format_caption(self, caption: str, figure_label: str, style: str, wrap_width: int) -> str:
        """Format caption according to specified style."""
        # Wrap text
        wrapped_text = textwrap.fill(caption, width=wrap_width)
        
        if style == "scientific":
            return f"**{figure_label}.** {wrapped_text}"
        elif style == "nature":
            return f"**{figure_label} |** {wrapped_text}"
        elif style == "ieee":
            return f"{figure_label}. {wrapped_text}"
        elif style == "apa":
            return f"*{figure_label}*\n{wrapped_text}"
        else:
            return f"{figure_label}. {wrapped_text}"
    
    def _format_panel_label(self, letter: str, style: str) -> str:
        """Format panel label according to style."""
        if style == "letter_bold":
            return f"**{letter}**"
        elif style == "letter_italic":
            return f"*{letter}*"
        elif style == "number":
            return f"**{ord(letter) - ord('A') + 1}**"
        else:
            return f"**{letter}**"
    
    def _add_caption_to_figure(self, fig, caption: str, position: str, width_ratio: float, font_size: Union[str, int]):
        """Add caption text to figure."""
        # Calculate position
        if position == "bottom":
            y_pos = 0.02
            va = 'bottom'
        else:  # top
            y_pos = 0.98
            va = 'top'
        
        # Add caption text
        fig.text(
            0.5, y_pos, caption,
            ha='center', va=va,
            fontsize=font_size,
            wrap=True,
            bbox=dict(boxstyle="round,pad=0.5", facecolor='white', alpha=0.8)
        )
        
        # Adjust layout to accommodate caption
        if position == "bottom":
            fig.subplots_adjust(bottom=0.15)
        else:
            fig.subplots_adjust(top=0.85)
    
    def _add_panel_label_to_axes(self, ax, label: str, position: str, font_size: Union[str, int], offset: Tuple[float, float]):
        """Add panel label to individual axes."""
        # Position mapping
        positions = {
            'top_left': (offset[0], offset[1]),
            'top_right': (1 - offset[0], offset[1]),
            'bottom_left': (offset[0], 1 - offset[1]),
            'bottom_right': (1 - offset[0], 1 - offset[1])
        }
        
        x_pos, y_pos = positions.get(position, (offset[0], offset[1]))
        
        # Determine alignment
        ha = 'left' if 'left' in position else 'right'
        va = 'top' if 'top' in position else 'bottom'
        
        # Add label
        ax.text(
            x_pos, y_pos, label,
            transform=ax.transAxes,
            fontsize=font_size,
            fontweight='bold',
            ha=ha, va=va,
            bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.9)
        )
    
    def _combine_panel_and_main_captions(self, panel_dict: Dict[str, str], main_caption: str) -> str:
        """Combine panel captions with main caption."""
        panel_descriptions = []
        for letter in sorted(panel_dict.keys()):
            panel_descriptions.append(f"({letter}) {panel_dict[letter].split(' ', 1)[1]}")  # Remove the bold letter
        
        combined = main_caption
        if panel_descriptions:
            combined += " " + " ".join(panel_descriptions)
        
        return combined
    
    def _save_caption_to_file(self, caption: str, figure_label: str, file_path: str = None):
        """Save caption to a text file."""
        if file_path is None:
            file_path = f"{figure_label.lower().replace(' ', '_')}_caption.txt"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(caption)
    
    def export_all_captions(self, file_path: str = "figure_captions.txt", style: str = "scientific"):
        """Export all registered captions to a file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("Figure Captions\n")
            f.write("=" * 50 + "\n\n")
            
            for label, info in self.caption_registry.items():
                f.write(f"{info['formatted']}\n\n")
    
    def get_cross_reference(self, figure_label: str) -> str:
        """Get a cross-reference string for a figure."""
        if figure_label in self.caption_registry:
            return f"(see {figure_label})"
        else:
            return f"(see {figure_label} - not found)"


# Global caption manager instance
caption_manager = ScientificCaption()


# Convenience functions
def add_figure_caption(fig, caption: str, **kwargs) -> str:
    """Convenience function to add figure caption."""
    return caption_manager.add_figure_caption(fig, caption, **kwargs)


def add_panel_captions(fig, axes, panel_captions, **kwargs) -> Dict[str, str]:
    """Convenience function to add panel captions."""
    return caption_manager.add_panel_captions(fig, axes, panel_captions, **kwargs)


def export_captions(file_path: str = "figure_captions.txt"):
    """Convenience function to export all captions."""
    return caption_manager.export_all_captions(file_path)


def cross_ref(figure_label: str) -> str:
    """Convenience function for cross-references."""
    return caption_manager.get_cross_reference(figure_label)


# Integration with scitex save system
def save_with_caption(fig, filename: str, caption: str = None, **caption_kwargs):
    """
    Save figure with caption integration.
    
    This function saves the figure and optionally creates caption files
    that can be used for manuscript preparation.
    """
    import scitex
    
    # Save the figure normally
    scitex.io.save(fig, filename)
    
    # Add caption if provided
    if caption:
        # Extract base filename
        base_name = filename.split('.')[0]
        
        # Save in multiple formats (like CSV system)
        _save_caption_multiple_formats(caption, base_name, **caption_kwargs)
        
        # Add caption to figure
        formatted_caption = add_figure_caption(fig, caption, **caption_kwargs)
        
        return formatted_caption
    
    return None


def _save_caption_multiple_formats(
    caption: str, 
    base_filename: str, 
    figure_label: str = None,
    style: str = "scientific",
    save_txt: bool = True,
    save_tex: bool = True,
    save_md: bool = True,
    wrap_width: int = 80
):
    """
    Save caption in multiple formats (like how scitex saves CSV data).
    
    Parameters
    ----------
    caption : str
        The caption text
    base_filename : str
        Base filename without extension
    figure_label : str, optional
        Figure label (auto-generated if None)
    style : str, optional
        Caption style, by default "scientific"
    save_txt : bool, optional
        Save as plain text, by default True
    save_tex : bool, optional
        Save as LaTeX, by default True
    save_md : bool, optional
        Save as Markdown, by default True
    wrap_width : int, optional
        Text wrapping width, by default 80
    """
    # Generate figure label if not provided
    if figure_label is None:
        caption_manager.figure_counter += 1
        figure_label = f"Figure {caption_manager.figure_counter}"
    
    # Create formatted versions
    txt_caption = _format_caption_for_txt(caption, figure_label, style, wrap_width)
    tex_caption = _format_caption_for_tex(caption, figure_label, style, wrap_width)
    md_caption = _format_caption_for_md(caption, figure_label, style, wrap_width)
    
    # Save files (following scitex naming convention)
    if save_txt:
        txt_file = f"{base_filename}_caption.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(txt_caption)
        print(f"📝 Caption saved to: {txt_file}")
    
    if save_tex:
        tex_file = f"{base_filename}_caption.tex"
        with open(tex_file, 'w', encoding='utf-8') as f:
            f.write(tex_caption)
        print(f"📝 LaTeX caption saved to: {tex_file}")
    
    if save_md:
        md_file = f"{base_filename}_caption.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_caption)
        print(f"📝 Markdown caption saved to: {md_file}")


def _format_caption_for_txt(caption: str, figure_label: str, style: str, wrap_width: int) -> str:
    """Format caption for plain text file."""
    wrapped_text = textwrap.fill(caption, width=wrap_width)
    
    if style == "scientific":
        return f"{figure_label}. {wrapped_text}"
    elif style == "nature":
        return f"{figure_label} | {wrapped_text}"
    elif style == "ieee":
        return f"{figure_label}. {wrapped_text}"
    elif style == "apa":
        return f"{figure_label}\n{wrapped_text}"
    else:
        return f"{figure_label}. {wrapped_text}"


def _format_caption_for_tex(caption: str, figure_label: str, style: str, wrap_width: int) -> str:
    """Format caption for LaTeX file."""
    # Escape special LaTeX characters
    tex_caption = _escape_latex(caption)
    wrapped_text = textwrap.fill(tex_caption, width=wrap_width)
    
    if style == "scientific":
        latex_caption = f"""% {figure_label} caption
\\begin{{figure}}[htbp]
    \\centering
    % \\includegraphics{{figure_filename}}
    \\caption{{\\textbf{{{figure_label}.}} {wrapped_text}}}
    \\label{{fig:{figure_label.lower().replace(' ', '_')}}}
\\end{{figure}}

% For use in manuscript:
% \\textbf{{{figure_label}.}} {wrapped_text}
"""
    elif style == "nature":
        latex_caption = f"""% {figure_label} caption (Nature style)
\\begin{{figure}}[htbp]
    \\centering
    % \\includegraphics{{figure_filename}}
    \\caption{{\\textbf{{{figure_label} |}} {wrapped_text}}}
    \\label{{fig:{figure_label.lower().replace(' ', '_')}}}
\\end{{figure}}
"""
    else:
        latex_caption = f"""% {figure_label} caption
\\begin{{figure}}[htbp]
    \\centering
    % \\includegraphics{{figure_filename}}
    \\caption{{{figure_label}. {wrapped_text}}}
    \\label{{fig:{figure_label.lower().replace(' ', '_')}}}
\\end{{figure}}
"""
    
    return latex_caption


def _format_caption_for_md(caption: str, figure_label: str, style: str, wrap_width: int) -> str:
    """Format caption for Markdown file."""
    wrapped_text = textwrap.fill(caption, width=wrap_width)
    
    if style == "scientific":
        return f"""# {figure_label}

**{figure_label}.** {wrapped_text}

---

*Generated by scitex scientific caption system*
"""
    elif style == "nature":
        return f"""# {figure_label}

**{figure_label} |** {wrapped_text}

---

*Generated by scitex scientific caption system*
"""
    else:
        return f"""# {figure_label}

{figure_label}. {wrapped_text}

---

*Generated by scitex scientific caption system*
"""


def _escape_latex(text: str) -> str:
    """Escape special LaTeX characters."""
    # Basic LaTeX character escaping
    escapes = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '^': r'\textasciicircum{}',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '\\': r'\textbackslash{}'
    }
    
    result = text
    for char, escape in escapes.items():
        result = result.replace(char, escape)
    
    return result


# Enhanced integration with scitex.io.save
def enhance_scitex_save_with_captions():
    """
    Enhance the scitex.io.save system to automatically handle captions.
    
    This can be called to monkey-patch scitex.io.save to include caption support.
    """
    import scitex
    
    # Store original save function
    original_save = scitex.io.save
    
    def enhanced_save(obj, filename, caption=None, **kwargs):
        """Enhanced save function with caption support."""
        # Call original save
        result = original_save(obj, filename, **kwargs)
        
        # Handle captions if provided
        if caption is not None and hasattr(obj, 'savefig'):  # It's a figure
            base_name = filename.split('.')[0]
            _save_caption_multiple_formats(caption, base_name)
        
        return result
    
    # Replace the save function
    scitex.io.save = enhanced_save
    print("📝 scitex.io.save enhanced with caption support!")
    print("Usage: scitex.io.save(fig, 'filename.png', caption='Your caption here')")


# Advanced caption utilities
def create_figure_list(output_file: str = "figure_list.txt", format: str = "txt"):
    """
    Create a comprehensive list of all figures and their captions.
    
    Parameters
    ----------
    output_file : str, optional
        Output filename, by default "figure_list.txt"
    format : str, optional
        Output format: "txt", "tex", "md", by default "txt"
    """
    if not caption_manager.caption_registry:
        print("No figures with captions found.")
        return
    
    if format == "tex":
        _create_latex_figure_list(output_file)
    elif format == "md":
        _create_markdown_figure_list(output_file)
    else:
        _create_text_figure_list(output_file)
    
    print(f"📋 Figure list saved to: {output_file}")


def _create_text_figure_list(output_file: str):
    """Create plain text figure list."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Figure List\n")
        f.write("=" * 50 + "\n\n")
        
        for label, info in caption_manager.caption_registry.items():
            f.write(f"{info['formatted']}\n\n")


def _create_latex_figure_list(output_file: str):
    """Create LaTeX figure list."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("% Figure List - Generated by scitex\n")
        f.write("\\section{List of Figures}\n\n")
        
        for label, info in caption_manager.caption_registry.items():
            escaped_caption = _escape_latex(info['text'])
            f.write(f"\\textbf{{{label}.}} {escaped_caption}\\\\\n\n")


def _create_markdown_figure_list(output_file: str):
    """Create Markdown figure list."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Figure List\n\n")
        f.write("*Generated by scitex scientific caption system*\n\n")
        
        for label, info in caption_manager.caption_registry.items():
            f.write(f"**{label}.** {info['text']}\n\n")


# Convenience function for quick caption addition
def quick_caption(fig, caption: str, save_path: str = None, **kwargs):
    """
    Quick way to add caption and save all formats.
    
    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to caption
    caption : str
        Caption text
    save_path : str, optional
        Base path for saving (uses figure number if None)
    **kwargs
        Additional arguments for caption formatting
    """
    if save_path is None:
        save_path = f"figure_{caption_manager.figure_counter + 1}"
    
    # Save in all formats
    _save_caption_multiple_formats(caption, save_path, **kwargs)
    
    # Add visual caption to figure
    return add_figure_caption(fig, caption, **kwargs)


# EOF