#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-07 08:15:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/io/_load_modules/test__xml.py

"""Comprehensive tests for XML file loading functionality.

This module provides extensive tests for the _load_xml function which converts
XML files to Python dictionaries. Tests cover basic functionality, error handling,
edge cases, and real-world XML patterns.
"""

import os
import tempfile
import pytest
import xml.etree.ElementTree as ET
from unittest.mock import patch, Mock


class TestLoadXml:
    """Test the _load_xml function."""

    def test_load_xml_basic(self):
        """Test loading basic XML file."""
        from scitex.io._load_modules import _load_xml
        
        xml_content = """<?xml version="1.0"?>
        <root>
            <child name="test">Value</child>
            <child2>Value2</child2>
        </root>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name
        
        try:
            result = _load_xml(temp_path)
            assert isinstance(result, dict)
            assert 'child' in result or 'child2' in result
        finally:
            os.unlink(temp_path)

    def test_load_xml_invalid_extension(self):
        """Test loading non-XML file raises ValueError."""
        from scitex.io._load_modules import _load_xml
        
        with pytest.raises(ValueError, match="File must have .xml extension"):
            _load_xml("file.txt")

    def test_load_xml_with_extension_variations(self):
        """Test various file extensions."""
        from scitex.io._load_modules import _load_xml
        
        # Valid extensions
        xml_content = """<?xml version="1.0"?><root><test>value</test></root>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name
        
        try:
            result = _load_xml(temp_path)
            assert isinstance(result, dict)
        finally:
            os.unlink(temp_path)
        
        # Invalid extensions
        invalid_extensions = ['.txt', '.json', '.yaml', '.xmlx', '.xm']
        for ext in invalid_extensions:
            with pytest.raises(ValueError):
                _load_xml(f"file{ext}")

    def test_load_xml_nonexistent_file(self):
        """Test loading non-existent XML file."""
        from scitex.io._load_modules import _load_xml
        
        # Should raise an error when trying to parse non-existent file
        with pytest.raises((FileNotFoundError, ET.ParseError)):
            _load_xml("nonexistent_file.xml")

    def test_load_xml_malformed_xml(self):
        """Test loading malformed XML file."""
        from scitex.io._load_modules import _load_xml
        
        xml_content = """<?xml version="1.0"?>
        <root>
            <unclosed_tag>
        </root>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name
        
        try:
            with pytest.raises(ET.ParseError):
                _load_xml(temp_path)
        finally:
            os.unlink(temp_path)

    def test_load_xml_with_attributes(self):
        """Test XML with attributes."""
        from scitex.io._load_modules import _load_xml
        
        xml_content = """<?xml version="1.0"?>
        <root version="1.0">
            <item id="1" type="test">Value1</item>
        </root>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name
        
        try:
            result = _load_xml(temp_path)
            assert isinstance(result, dict)
            assert 'version' in result  # Root attribute
            assert result['version'] == '1.0'
        finally:
            os.unlink(temp_path)

    def test_load_xml_nested_structure(self):
        """Test XML with nested structure."""
        from scitex.io._load_modules import _load_xml
        
        xml_content = """<?xml version="1.0"?>
        <config>
            <database>
                <host>localhost</host>
                <port>5432</port>
            </database>
        </config>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name
        
        try:
            result = _load_xml(temp_path)
            assert isinstance(result, dict)
            assert 'database' in result
            assert isinstance(result['database'], dict)
            assert 'host' in result['database']
            assert result['database']['host'] == 'localhost'
        finally:
            os.unlink(temp_path)

    def test_load_xml_with_text_content(self):
        """Test XML with simple text content."""
        from scitex.io._load_modules import _load_xml
        
        xml_content = """<?xml version="1.0"?>
        <root>
            <name>John</name>
            <age>30</age>
        </root>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name
        
        try:
            result = _load_xml(temp_path)
            assert isinstance(result, dict)
            assert 'name' in result
            assert 'age' in result
            assert result['name'] == 'John'
            assert result['age'] == '30'
        finally:
            os.unlink(temp_path)

    def test_load_xml_with_repeated_elements(self):
        """Test XML with repeated elements."""
        from scitex.io._load_modules import _load_xml
        
        xml_content = """<?xml version="1.0"?>
        <items>
            <item>Item1</item>
            <item>Item2</item>
            <item>Item3</item>
        </items>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name
        
        try:
            result = _load_xml(temp_path)
            assert isinstance(result, dict)
            assert 'item' in result
            # Should handle repeated elements (as list or similar structure)
            items = result['item']
            assert items is not None
        finally:
            os.unlink(temp_path)

    def test_load_xml_empty_elements(self):
        """Test XML with empty elements."""
        from scitex.io._load_modules import _load_xml
        
        xml_content = """<?xml version="1.0"?>
        <root>
            <empty_element></empty_element>
            <with_text>Some text</with_text>
        </root>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name
        
        try:
            result = _load_xml(temp_path)
            assert isinstance(result, dict)
            assert 'with_text' in result
            assert result['with_text'] == 'Some text'
        finally:
            os.unlink(temp_path)

    def test_load_xml_mixed_content(self):
        """Test XML with mixed content types."""
        from scitex.io._load_modules import _load_xml
        
        xml_content = """<?xml version="1.0"?>
        <root>
            <simple>Text</simple>
            <with_attr id="123">Text with attr</with_attr>
            <nested>
                <child>Nested text</child>
            </nested>
        </root>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name
        
        try:
            result = _load_xml(temp_path)
            assert isinstance(result, dict)
            assert 'simple' in result
            assert 'with_attr' in result
            assert 'nested' in result
            assert result['simple'] == 'Text'
        finally:
            os.unlink(temp_path)

    def test_load_xml_function_signature(self):
        """Test that _load_xml function has correct signature."""
        from scitex.io._load_modules import _load_xml
        import inspect
        
        sig = inspect.signature(_load_xml)
        params = list(sig.parameters.keys())
        assert 'lpath' in params
        assert 'kwargs' in params or len([p for p in sig.parameters.values() if p.kind == p.VAR_KEYWORD]) > 0

    def test_load_xml_docstring(self):
        """Test that _load_xml function has a docstring."""
        from scitex.io._load_modules import _load_xml
        
        assert _load_xml.__doc__ is not None
        assert len(_load_xml.__doc__.strip()) > 0
        assert 'XML' in _load_xml.__doc__

    def test_load_xml_return_type(self):
        """Test that _load_xml returns a dictionary."""
        from scitex.io._load_modules import _load_xml
        
        xml_content = """<?xml version="1.0"?><root><test>value</test></root>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name
        
        try:
            result = _load_xml(temp_path)
            assert isinstance(result, dict)
            assert len(result) > 0
        finally:
            os.unlink(temp_path)

    def test_load_xml_complex_structure(self):
        """Test complex XML structure."""
        from scitex.io._load_modules import _load_xml
        
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <configuration version="2.0">
            <metadata>
                <title>Test Configuration</title>
                <author email="test@example.com">Test Author</author>
            </metadata>
            <settings>
                <database>
                    <host>localhost</host>
                    <port>5432</port>
                </database>
                <features>
                    <feature name="logging" enabled="true"/>
                    <feature name="caching" enabled="false"/>
                </features>
            </settings>
        </configuration>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name
        
        try:
            result = _load_xml(temp_path)
            assert isinstance(result, dict)
            
            # Test root attributes
            assert 'version' in result
            assert result['version'] == '2.0'
            
            # Test nested structure
            assert 'metadata' in result
            assert 'settings' in result
            
            # Test metadata
            metadata = result['metadata']
            assert 'title' in metadata
            assert metadata['title'] == 'Test Configuration'
            
        finally:
            os.unlink(temp_path)

    def test_load_xml_special_characters(self):
        """Test XML with special characters."""
        from scitex.io._load_modules import _load_xml
        
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <root>
            <text>Content with &amp; special &lt; characters &gt;</text>
            <unicode>Unicode: ñáéíóú</unicode>
        </root>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False, encoding='utf-8') as f:
            f.write(xml_content)
            temp_path = f.name
        
        try:
            result = _load_xml(temp_path)
            assert isinstance(result, dict)
            assert 'text' in result
            assert 'unicode' in result
        finally:
            os.unlink(temp_path)

    def test_load_xml_real_world_patterns(self):
        """Test common real-world XML patterns."""
        from scitex.io._load_modules import _load_xml
        
        # RSS-like structure
        xml_content = """<?xml version="1.0"?>
        <rss version="2.0">
            <channel>
                <title>Test RSS</title>
                <item>
                    <title>Item 1</title>
                    <description>Description 1</description>
                </item>
            </channel>
        </rss>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name
        
        try:
            result = _load_xml(temp_path)
            assert isinstance(result, dict)
            assert 'version' in result
            assert 'channel' in result
        finally:
            os.unlink(temp_path)

    def test_load_xml_error_handling(self):
        """Test error handling for various edge cases."""
        from scitex.io._load_modules import _load_xml
        
        # Empty string path
        with pytest.raises(ValueError):
            _load_xml("")
        
        # Path with wrong extension
        with pytest.raises(ValueError):
            _load_xml("file.json")
        
        # Path without extension
        with pytest.raises(ValueError):
            _load_xml("file")

    def test_load_xml_kwargs_handling(self):
        """Test that kwargs parameter exists even if not used."""
        from scitex.io._load_modules import _load_xml
        
        xml_content = """<?xml version="1.0"?><root><test>value</test></root>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name
        
        try:
            # Should not raise error even with unused kwargs
            result = _load_xml(temp_path, unused_arg=True, another_arg="test")
            assert isinstance(result, dict)
        finally:
            os.unlink(temp_path)


class TestLoadXmlAdvancedFeatures:
    """Test advanced XML features and edge cases."""
    
    def test_load_xml_cdata_sections(self):
        """Test XML with CDATA sections."""
        from scitex.io._load_modules import _load_xml
        
        xml_content = """<?xml version="1.0"?>
        <root>
            <code><![CDATA[if (x < 10 && y > 5) { return true; }]]></code>
            <normal>Normal text</normal>
        </root>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name
        
        try:
            result = _load_xml(temp_path)
            assert isinstance(result, dict)
            # CDATA content should be preserved
            if 'code' in result:
                assert 'if' in str(result.get('code', ''))
        finally:
            os.unlink(temp_path)
    
    def test_load_xml_comments_handling(self):
        """Test XML with comments."""
        from scitex.io._load_modules import _load_xml
        
        xml_content = """<?xml version="1.0"?>
        <root>
            <!-- This is a comment -->
            <data>value</data>
            <!-- Another comment -->
        </root>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name
        
        try:
            result = _load_xml(temp_path)
            assert isinstance(result, dict)
            assert 'data' in result
            assert result['data'] == 'value'
        finally:
            os.unlink(temp_path)
    
    def test_load_xml_namespaces(self):
        """Test XML with namespaces."""
        from scitex.io._load_modules import _load_xml
        
        xml_content = """<?xml version="1.0"?>
        <root xmlns:ns="http://example.com/namespace">
            <ns:element>Namespaced content</ns:element>
            <regular>Regular content</regular>
        </root>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name
        
        try:
            result = _load_xml(temp_path)
            assert isinstance(result, dict)
            # Should handle namespaced elements somehow
            assert 'regular' in result
        finally:
            os.unlink(temp_path)
    
    def test_load_xml_processing_instructions(self):
        """Test XML with processing instructions."""
        from scitex.io._load_modules import _load_xml
        
        xml_content = """<?xml version="1.0"?>
        <?xml-stylesheet type="text/xsl" href="style.xsl"?>
        <root>
            <data>value</data>
        </root>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name
        
        try:
            result = _load_xml(temp_path)
            assert isinstance(result, dict)
            assert 'data' in result
        finally:
            os.unlink(temp_path)
    
    def test_load_xml_whitespace_preservation(self):
        """Test whitespace handling in XML."""
        from scitex.io._load_modules import _load_xml
        
        xml_content = """<?xml version="1.0"?>
        <root>
            <preserved>  Multiple   spaces  </preserved>
            <trimmed>
                Line breaks
                and indentation
            </trimmed>
        </root>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name
        
        try:
            result = _load_xml(temp_path)
            assert isinstance(result, dict)
            # Check if whitespace is stripped (as per the implementation)
            if 'preserved' in result:
                assert result['preserved'] == 'Multiple   spaces'
        finally:
            os.unlink(temp_path)


class TestLoadXmlStressTests:
    """Stress tests for XML loading."""
    
    def test_load_xml_large_file(self):
        """Test loading large XML file."""
        from scitex.io._load_modules import _load_xml
        
        # Generate large XML content
        xml_content = '<?xml version="1.0"?>\n<root>\n'
        for i in range(1000):
            xml_content += f'    <item id="{i}">Item {i} content</item>\n'
        xml_content += '</root>'
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name
        
        try:
            result = _load_xml(temp_path)
            assert isinstance(result, dict)
            assert 'item' in result
        finally:
            os.unlink(temp_path)
    
    def test_load_xml_deeply_nested(self):
        """Test deeply nested XML structure."""
        from scitex.io._load_modules import _load_xml
        
        # Generate deeply nested XML
        depth = 50
        xml_content = '<?xml version="1.0"?>\n'
        for i in range(depth):
            xml_content += '<level' + str(i) + '>'
        xml_content += 'Deep value'
        for i in range(depth-1, -1, -1):
            xml_content += '</level' + str(i) + '>'
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_path = f.name
        
        try:
            result = _load_xml(temp_path)
            assert isinstance(result, dict)
            # Should handle deep nesting
            current = result
            for i in range(min(10, depth)):  # Check first 10 levels
                key = 'level' + str(i)
                if key in current:
                    current = current[key]
        finally:
            os.unlink(temp_path)


class TestLoadXmlRealWorldExamples:
    """Test with real-world XML examples."""
    
    def test_load_xml_svg_file(self):
        """Test loading SVG XML file."""
        from scitex.io._load_modules import _load_xml
        
        svg_content = """<?xml version="1.0"?>
        <svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
            <circle cx="50" cy="50" r="40" fill="red"/>
            <text x="50" y="55" text-anchor="middle">SVG</text>
        </svg>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(svg_content)
            temp_path = f.name
        
        try:
            result = _load_xml(temp_path)
            assert isinstance(result, dict)
            assert 'width' in result
            assert 'height' in result
        finally:
            os.unlink(temp_path)
    
    def test_load_xml_configuration_file(self):
        """Test loading configuration-style XML."""
        from scitex.io._load_modules import _load_xml
        
        config_content = """<?xml version="1.0" encoding="UTF-8"?>
        <configuration>
            <appSettings>
                <add key="ConnectionString" value="Server=localhost;Database=test;"/>
                <add key="MaxRetries" value="3"/>
            </appSettings>
            <system.web>
                <compilation debug="true" targetFramework="4.5"/>
                <httpRuntime maxRequestLength="4096"/>
            </system.web>
        </configuration>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(config_content)
            temp_path = f.name
        
        try:
            result = _load_xml(temp_path)
            assert isinstance(result, dict)
            assert 'appSettings' in result or 'system.web' in result
        finally:
            os.unlink(temp_path)

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_load_modules/_xml.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-14 07:55:49 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/io/_load_modules/_xml.py
# 
# 
# def _load_xml(lpath, **kwargs):
#     """Load XML file and convert to dict."""
#     if not lpath.endswith(".xml"):
#         raise ValueError("File must have .xml extension")
#     
#     # Import xml2dict locally to avoid circular imports
#     from xml.etree import cElementTree as ElementTree
#     
#     # Inline the xml2dict functionality to avoid circular import
#     tree = ElementTree.parse(lpath)
#     root = tree.getroot()
#     
#     # Simplified XML to dict conversion - basic implementation
#     def xml_element_to_dict(element):
#         result = {}
#         
#         # Add attributes
#         if element.attrib:
#             result.update(element.attrib)
#         
#         # Handle child elements
#         for child in element:
#             if child.tag in result:
#                 # Convert to list if multiple elements with same tag
#                 if not isinstance(result[child.tag], list):
#                     result[child.tag] = [result[child.tag]]
#                 result[child.tag].append(xml_element_to_dict(child))
#             else:
#                 result[child.tag] = xml_element_to_dict(child)
#         
#         # Handle text content
#         if element.text and element.text.strip():
#             if result:
#                 result['text'] = element.text.strip()
#             else:
#                 return element.text.strip()
#         
#         return result
#     
#     return xml_element_to_dict(root)
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_load_modules/_xml.py
# --------------------------------------------------------------------------------
