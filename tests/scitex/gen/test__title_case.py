#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-31 22:30:00 (claude)"
# File: ./tests/scitex/gen/test__title_case.py

"""
Comprehensive tests for scitex.gen._title_case module.

This module tests:
- title_case function with various text inputs
- Handling of prepositions, articles, and conjunctions
- Acronym preservation
- Edge cases
"""

import pytest

from scitex.gen import title_case



class TestTitleCaseBasic:
    """Test basic title_case functionality."""

    def test_simple_sentence(self):
        """Test title case conversion of simple sentence."""

        result = title_case("hello world")
        assert result == "Hello World"

    def test_with_lowercase_words(self):
        """Test that certain words remain lowercase."""

        result = title_case("the cat and the dog")
        assert result == "The Cat and the Dog"

    def test_documentation_example(self):
        """Test the example from the docstring."""

        text = "welcome to the world of ai and using CPUs for gaming"
        result = title_case(text)
        assert result == "Welcome to the World of AI and Using CPUs for Gaming"

    def test_single_word(self):
        """Test title case with single word."""

        assert title_case("hello") == "Hello"
        assert title_case("HELLO") == "HELLO"  # Preserves acronyms
        assert title_case("h") == "H"  # Single char capitalized

    def test_empty_string(self):
        """Test title case with empty string."""

        assert title_case("") == ""


class TestTitleCasePrepositions:
    """Test handling of prepositions, conjunctions, and articles."""

    def test_all_lowercase_words(self):
        """Test all words that should remain lowercase."""

        lowercase_words = [
            "a",
            "an",
            "the",
            "and",
            "but",
            "or",
            "nor",
            "at",
            "by",
            "to",
            "in",
            "with",
            "of",
            "on",
        ]

        for word in lowercase_words:
            text = f"something {word} something"
            result = title_case(text)
            assert f" {word} " in result

    def test_prepositions_at_start(self):
        """Test prepositions at the start of text."""

        # These should be capitalized when at the beginning
        assert title_case("the beginning") == "The Beginning"
        assert title_case("and then") == "And Then"
        assert title_case("of mice") == "Of Mice"

    def test_multiple_prepositions(self):
        """Test text with multiple prepositions."""

        text = "the cat in the hat with a bat"
        result = title_case(text)
        assert result == "The Cat in the Hat with a Bat"

    def test_consecutive_lowercase_words(self):
        """Test consecutive lowercase words."""

        text = "this and or that"
        result = title_case(text)
        assert result == "This and or That"


class TestTitleCaseAcronyms:
    """Test handling of acronyms and uppercase words."""

    def test_single_acronym(self):
        """Test preservation of single acronym."""

        assert title_case("using AI technology") == "Using AI Technology"
        assert title_case("the CPU speed") == "The CPU Speed"
        assert title_case("NASA mission") == "NASA Mission"

    def test_multiple_acronyms(self):
        """Test text with multiple acronyms."""

        text = "FBI and CIA with NSA"
        result = title_case(text)
        assert result == "FBI and CIA with NSA"

    def test_mixed_case_acronyms(self):
        """Test that only fully uppercase words are treated as acronyms."""

        # Mixed case should be normalized
        assert title_case("iPhone") == "Iphone"
        assert title_case("eBay") == "Ebay"

        # But full uppercase preserved
        assert title_case("IPHONE") == "IPHONE"
        assert title_case("EBAY") == "EBAY"

    def test_single_letter_handling(self):
        """Test handling of single uppercase letters."""

        # Single letters are not considered acronyms
        assert title_case("I am here") == "I Am Here"
        assert title_case("a B c") == "A B C"
        assert title_case("X marks") == "X Marks"

    def test_numbers_with_letters(self):
        """Test handling of alphanumeric combinations."""

        assert (
            title_case("3D printing") == "3d Printing"
        )  # Not uppercase, so normalized
        assert title_case("3D PRINTING") == "3D PRINTING"  # Both preserved as acronyms


class TestTitleCaseEdgeCases:
    """Test edge cases and special scenarios."""

    def test_punctuation(self):
        """Test title case with punctuation."""

        assert title_case("hello, world!") == "Hello, World!"
        assert title_case("what's up?") == "What's Up?"
        assert title_case("mother-in-law") == "Mother-in-law"

    def test_extra_spaces(self):
        """Test handling of extra spaces."""

        # Note: split() will collapse multiple spaces
        assert title_case("hello  world") == "Hello World"
        assert title_case("   the   cat   ") == "The Cat"

    def test_tabs_and_newlines(self):
        """Test handling of tabs and newlines."""

        # split() without args splits on any whitespace
        assert title_case("hello\tworld") == "Hello World"
        assert title_case("hello\nworld") == "Hello World"

    def test_mixed_whitespace(self):
        """Test mixed whitespace characters."""

        text = "the\tcat\nand   the\r\ndog"
        result = title_case(text)
        assert result == "The Cat and the Dog"

    def test_unicode_text(self):
        """Test with unicode characters."""

        assert title_case("café au lait") == "Café Au Lait"
        assert title_case("naïve approach") == "Naïve Approach"

    def test_all_uppercase_input(self):
        """Test with all uppercase input."""

        # Multi-char uppercase words are preserved
        text = "THE QUICK BROWN FOX"
        result = title_case(text)
        assert result == "THE QUICK BROWN FOX"

    def test_all_lowercase_input(self):
        """Test with all lowercase input."""

        text = "the quick brown fox"
        result = title_case(text)
        assert result == "The Quick Brown Fox"


class TestTitleCaseRealWorld:
    """Test with real-world examples."""

    def test_book_titles(self):
        """Test with book title examples."""

        titles = [
            ("the lord of the rings", "The Lord of the Rings"),
            ("war and peace", "War and Peace"),
            ("to kill a mockingbird", "To Kill a Mockingbird"),
            ("of mice and men", "Of Mice and Men"),
        ]

        for input_title, expected in titles:
            assert title_case(input_title) == expected

    def test_technical_titles(self):
        """Test with technical document titles."""

        titles = [
            ("introduction to AI and ML", "Introduction to AI and ML"),
            ("working with APIs in python", "Working with APIs in Python"),
            ("the future of IoT devices", "The Future of IOT Devices"),
        ]

        for input_title, expected in titles:
            assert title_case(input_title) == expected

    def test_mixed_content(self):
        """Test with mixed content types."""

        text = "using NASA data with the FBI database and CIA reports"
        result = title_case(text)
        assert result == "Using NASA Data with the FBI Database and CIA Reports"


class TestTitleCaseParameterized:
    """Parametrized tests for comprehensive coverage."""

    @pytest.mark.parametrize(
        "input_text,expected",
        [
            ("", ""),
            ("a", "A"),
            ("the", "The"),
            ("hello", "Hello"),
            ("HELLO", "HELLO"),
            ("hello world", "Hello World"),
            ("the cat", "The Cat"),
            ("cat and dog", "Cat and Dog"),
            ("FBI agent", "FBI Agent"),
            ("use of AI", "Use of AI"),
            ("AI and ML", "AI and ML"),
            ("the AI revolution", "The AI Revolution"),
        ],
    )
    def test_various_inputs(self, input_text, expected):
        """Test title_case with various inputs."""

        assert title_case(input_text) == expected

    @pytest.mark.parametrize(
        "preposition",
        [
            "a",
            "an",
            "the",
            "and",
            "but",
            "or",
            "nor",
            "at",
            "by",
            "to",
            "in",
            "with",
            "of",
            "on",
        ],
    )
    def test_preposition_handling(self, preposition):
        """Test that each preposition is handled correctly."""

        # In middle of sentence - should be lowercase
        text = f"word {preposition} word"
        result = title_case(text)
        assert result == f"Word {preposition} Word"

        # At start - should be capitalized
        text = f"{preposition} word"
        result = title_case(text)
        assert result == f"{preposition.capitalize()} Word"


class TestTitleCaseIntegration:
    """Integration tests for title_case function."""

    def test_complex_technical_text(self):
        """Test with complex technical text."""

        text = "building RESTful APIs with HTTP and JSON in the cloud"
        result = title_case(text)
        expected = "Building RESTFUL APIS with HTTP and JSON in the Cloud"
        assert result == expected

    def test_article_headline(self):
        """Test with article headline format."""

        text = "the rise of AI and the future of work in the digital age"
        result = title_case(text)
        expected = "The Rise of AI and the Future of Work in the Digital Age"
        assert result == expected

    def test_with_numbers_and_symbols(self):
        """Test with numbers and symbols."""

        text = "the top 10 tips for using AWS S3 and EC2"
        result = title_case(text)
        expected = "The Top 10 Tips for Using AWS S3 and EC2"
        assert result == expected


if __name__ == "__main__":
    # Run specific test file
    import os

    pytest.main([os.path.abspath(__file__), "-v"])
