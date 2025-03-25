# Configuration file for the Sphinx documentation builder.

project = 'Contacts API'
copyright = '2025, Igor Dykyi'
author = 'Igor Dykyi'
release = '1.0'

# Add paths and extensions
import os
import sys
sys.path.insert(0, os.path.abspath('../../'))

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'alabaster'
html_static_path = ['_static']
