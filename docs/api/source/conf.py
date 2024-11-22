# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import cracknuts
import os
import sys

sys.path.insert(0, os.path.abspath("../../../src/cracknuts"))  # 修改为你的项目路径
sys.path.insert(1, ".")

print(sys.path)

project = "CrackNuts"
copyright = "2024, CrackNuts"
author = "CrackNuts"
release = cracknuts.version()
version = release

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",  # 支持自动文档生成
    # 'sphinx.ext.napoleon',       # 支持 Google 和 NumPy 风格 docstring
    "sphinx.ext.autosummary",  # 可选：生成模块总结
    "sphinx_autodoc_typehints",  # 可选：显示类型注释
    # 'sphinx.ext.viewcode',
]

templates_path = ["_templates"]
exclude_patterns = []

language = "zh"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_title = "API Documentation"
# html_theme = 'alabaster'
# html_theme = 'sphinx_rtd_theme'
html_theme = "sphinxawesome_theme"
html_static_path = ["_static"]

html_favicon = '../../static/favicon.ico'

html_theme_options = {
    "logo_light": "../../static/logo2.svg",
    "logo_dark": "../../static/logo2.svg",
    "main_nav_links": {
        "CrackNuts": "/",
    },
}
