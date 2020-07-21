# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys

sys.path.insert(0, os.path.abspath('..'))

import energyquantified


# -- Project information -----------------------------------------------------

project = 'Energy Quantified'
copyright = 'Energy Quantified AS'
author = 'Energy Quantified'

version = energyquantified.__version__


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'recommonmark',
    'sphinx.ext.autodoc',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for autodoc -----------------------------------------------------

add_function_parentheses = False

# autoclass_content = "class" # Use "both" to both include class and __init__

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

html_theme_options = {
    'description': 'Python client for Energy Quantified\'s API.',
    'logo': 'eq.svg',
    'logo_name': True,
    'show_powered_by': False,
    'github_user': 'energyquantified',
    'github_repo': 'eq-python-client',
    'github_button': True,
    'github_banner': False,
}

# Default html_siderbars
#
#html_sidebars = {
#    "**": [
#        "about.html",
#        "navigation.html",
#        "relations.html",
#        "searchbox.html",
#        "donate.html",
#    ]
#}

html_sidebars = {
    "**": [
        "eq.html",
        "navigation.html",
        "relations.html",
        "searchbox.html",
    ]
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
