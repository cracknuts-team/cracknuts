# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import cracknuts
import os
import sys

sys.path.insert(0, os.path.abspath("../src/cracknuts"))  # 修改为你的项目路径
sys.path.insert(1, "")

project = "CrackNuts"
copyright = "2024, CrackNuts"
author = "CrackNuts"
release = cracknuts.version()
version = release

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx_autodoc_typehints",
    'sphinx.ext.viewcode',
    'sphinx.ext.doctest'
]

templates_path = ["_templates"]
exclude_patterns = []

language = "en"
languages = ['en', 'zh_CN']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_title = "CrackNuts API Documentation"
html_theme = 'sphinx_rtd_theme'

html_favicon = '../static/favicon.ico'

html_theme_options = {
}

autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'private-members': False,
    'special-members': '__init__',
    'inherited-members': False,
    'show-inheritance': True,
    'no-index': True,
}

locale_dirs = ['locale/']   # path is example but recommended.
gettext_compact = False     # optional