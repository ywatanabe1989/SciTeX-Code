#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-14 07:55:42 (ywatanabe)"
# File: ./scitex_repo/src/scitex/io/_load_modules/_markdown.py


def _load_markdown(lpath_md, style="plain_text", **kwargs):
    """
    Load and convert Markdown content from a file.

    This function reads a Markdown file and converts it to either HTML or plain text format.

    Parameters:
    -----------
    lpath_md : str
        The path to the Markdown file to be loaded.
    style : str, optional
        The output style of the converted content.
        Options are "html" or "plain_text" (default).

    Returns:
    --------
    str
        The converted content of the Markdown file, either as HTML or plain text.

    Raises:
    -------
    FileNotFoundError
        If the specified file does not exist.
    IOError
        If there's an error reading the file.
    ValueError
        If an invalid style option is provided.

    Notes:
    ------
    This function uses the 'markdown' library to convert Markdown to HTML,
    and 'html2text' to convert HTML to plain text when necessary.
    """
    import html2text
    import markdown

    # Load Markdown content from a file
    with open(lpath_md, "r") as file:
        markdown_content = file.read()

    # Convert Markdown to HTML
    html_content = markdown.markdown(markdown_content)
    if style == "html":
        return html_content
    elif style == "plain_text":
        text_maker = html2text.HTML2Text()
        text_maker.ignore_links = True
        text_maker.bypass_tables = False
        plain_text = text_maker.handle(html_content)
        return plain_text
    else:
        raise ValueError("Invalid style option. Choose 'html' or 'plain_text'.")


def load_markdown(lpath_md, style="plain_text"):
    """
    Load and convert a Markdown file to either HTML or plain text.

    Parameters:
    -----------
    lpath_md : str
        The path to the Markdown file.
    style : str, optional
        The output style, either "html" or "plain_text" (default).

    Returns:
    --------
    str
        The converted content of the Markdown file.
    """
    import html2text
    import markdown

    # Load Markdown content from a file
    with open(lpath_md, "r") as file:
        markdown_content = file.read()

    # Convert Markdown to HTML
    html_content = markdown.markdown(markdown_content)
    if style == "html":
        return html_content

    elif style == "plain_text":
        text_maker = html2text.HTML2Text()
        text_maker.ignore_links = True
        text_maker.bypass_tables = False
        plain_text = text_maker.handle(html_content)

        return plain_text


# def _load_markdown(lpath):
#     md_text = StringIO(lpath.read().decode("utf-8"))
#     html = markdown.markdown(md_text.read())
#     return html

# EOF
