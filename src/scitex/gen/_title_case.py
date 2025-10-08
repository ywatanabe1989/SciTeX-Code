#!./env/bin/python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-04-24 15:05:34"
# Author: Yusuke Watanabe (ywatanabe@scitex.ai)


"""
This script does XYZ.
"""


"""
Imports
"""
import sys

import matplotlib.pyplot as plt


"""
Config
"""
# CONFIG = scitex.gen.load_configs()


"""
Functions & Classes
"""


def title_case(text):
    """
    Converts a string to title case while keeping certain prepositions, conjunctions, and articles in lowercase,
    and ensuring words detected as potential acronyms (all uppercase) are fully capitalized.

    Parameters:
    - text (str): The text to convert to title case.

    Returns:
    - str: The converted text in title case with certain words in lowercase and potential acronyms fully capitalized.

    Examples:
    --------
        print(title_case("welcome to the world of ai and using CPUs for gaming"))  # Welcome to the World of AI and Using CPUs for Gaming
    """
    # List of words to keep in lowercase
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

    words = text.split()
    final_words = []
    for word in words:
        # Check if the word is fully in uppercase and more than one character, suggesting an acronym
        if word.isupper() and len(word) > 1:
            final_words.append(word)
        elif word.lower() in lowercase_words:
            final_words.append(word.lower())
        else:
            final_words.append(word.capitalize())
    return " ".join(final_words)


def main():
    # Example usage:
    text = "welcome to the world of ai and using CPUs for gaming"
    print(title_case(text))


if __name__ == "__main__":
    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.session.start(sys, plt, verbose=False)
    main()
    scitex.session.close(CONFIG, verbose=False, notify=False)

# EOF
