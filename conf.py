# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath('.'))
sys.path.append(os.path.abspath("./computations"))
sys.path.append(os.path.abspath("./help"))
sys.path.append(os.path.abspath("./metrics"))
sys.path.append(os.path.abspath("./exceptions"))
sys.path.append(os.path.abspath("./executions"))
sys.path.append(os.path.abspath("./tests"))

# -- Project information -----------------------------------------------------

project = 'Tester, Reviewer and Aggregator of the Use of Modules Applied to Scheduling'
copyright = '2020, Gautier Raimondi'
author = 'Gautier Raimondi'
language = 'en'

# The full version, including alpha/beta/rc tags
release = '0.1'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages'
]

todo_include_todos = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for LaTeX output------------------------------------------------

latex_engine = 'pdflatex'
latex_elements = {
    'papersize': 'a4paper',
    'releasename': 'TRAUMAS',
    'figure_align': 'htbp',
    'pointsize': '10pt',

}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = 'alabaster'
# html_theme = 'sphinx_rtd_theme'
