#!/usr/bin/env python3
"""Configuration for GenAI tests."""

# Import all fixtures from fixtures.py to make them available to all tests
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from fixtures import *
