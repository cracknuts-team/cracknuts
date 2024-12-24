# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import cracknuts
import os
import sys

sys.path.insert(0, os.path.abspath("../../src/cracknuts"))  # 修改为你的项目路径
sys.path.insert(1, "")

project = "CrackNuts"
copyright = "2024, CrackNuts"
author = "CrackNuts"
release = cracknuts.version()
version = release

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",  # 支持自动文档生成
    "sphinx.ext.autosummary",  # 可选：生成模块总结
    "sphinx_autodoc_typehints",  # 可选：显示类型注释
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
# html_theme = 'alabaster'
html_theme = 'sphinx_rtd_theme'
# html_theme = "sphinxawesome_theme"

html_favicon = '../static/favicon.ico'

html_theme_options = {
}

autodoc_default_options = {
    'members': True,  # 包括类成员
    'undoc-members': True,  # 包括未文档化的成员
    'private-members': False,  # 包括私有成员
    'special-members': '__init__',  # 包括特殊成员 (如 __init__)
    'inherited-members': False,  # 包括继承的成员
    'show-inheritance': True,  # 显示继承关系
    'no-index': True,  # 不生成索引
}

locale_dirs = ['locale/']   # path is example but recommended.
gettext_compact = False     # optional