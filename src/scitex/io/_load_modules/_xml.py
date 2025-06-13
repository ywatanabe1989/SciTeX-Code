#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-14 07:55:49 (ywatanabe)"
# File: ./scitex_repo/src/scitex/io/_load_modules/_xml.py


def _load_xml(lpath, **kwargs):
    """Load XML file and convert to dict."""
    if not lpath.endswith(".xml"):
        raise ValueError("File must have .xml extension")
    
    # Import xml2dict locally to avoid circular imports
    from xml.etree import cElementTree as ElementTree
    
    # Inline the xml2dict functionality to avoid circular import
    tree = ElementTree.parse(lpath)
    root = tree.getroot()
    
    # Simplified XML to dict conversion - basic implementation
    def xml_element_to_dict(element):
        result = {}
        
        # Add attributes
        if element.attrib:
            result.update(element.attrib)
        
        # Handle child elements
        for child in element:
            if child.tag in result:
                # Convert to list if multiple elements with same tag
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(xml_element_to_dict(child))
            else:
                result[child.tag] = xml_element_to_dict(child)
        
        # Handle text content
        if element.text and element.text.strip():
            if result:
                result['text'] = element.text.strip()
            else:
                return element.text.strip()
        
        return result
    
    return xml_element_to_dict(root)


# EOF
