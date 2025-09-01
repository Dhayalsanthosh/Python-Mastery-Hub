# File: docs/source/conf.py

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from datetime import datetime

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.abspath('../../src'))

# -- Project information -----------------------------------------------------

project = 'Python Mastery Hub'
copyright = f'2024-{datetime.now().year}, Python Mastery Hub Team'
author = 'Python Mastery Hub Team'
release = '1.0.0'
version = '1.0.0'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx.ext.napoleon',
    'sphinx_rtd_theme',
    'myst_parser',
    'nbsphinx',
    'sphinx_copybutton',
    'sphinx_design',
    'sphinxcontrib.mermaid',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    '_build',
    'Thumbs.db',
    '.DS_Store',
    '**.ipynb_checkpoints',
    'notebooks/.ipynb_checkpoints',
]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'sphinx_rtd_theme'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    'canonical_url': '',
    'analytics_id': '',
    'analytics_anonymize_ip': False,
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'vcs_pageview_mode': '',
    'style_nav_header_background': '#2980B9',
    # Toc options
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
html_sidebars = {
    '**': [
        'relations.html',  # needs 'show_related': True theme option to display
        'searchbox.html',
    ]
}

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = '../assets/images/logo.png'

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
html_favicon = '../assets/images/favicon.ico'

# Output file base name for HTML help builder.
htmlhelp_basename = 'PythonMasteryHubdoc'

# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    'papersize': 'letterpaper',
    
    # The font size ('10pt', '11pt' or '12pt').
    'pointsize': '10pt',
    
    # Additional stuff for the LaTeX preamble.
    'preamble': '',
    
    # Latex figure (float) alignment
    'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    ('index', 'PythonMasteryHub.tex', 'Python Mastery Hub Documentation',
     'Python Mastery Hub Team', 'manual'),
]

# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', 'pythonmasteryhub', 'Python Mastery Hub Documentation',
     [author], 1)
]

# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    ('index', 'PythonMasteryHub', 'Python Mastery Hub Documentation',
     author, 'PythonMasteryHub', 'Interactive Python learning platform.',
     'Miscellaneous'),
]

# -- Options for Epub output -------------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
epub_identifier = 'https://github.com/python-mastery-hub/python-mastery-hub'

# A unique identification for the text.
epub_uid = 'pythonmasteryhub'

# A list of files that should not be packed into the epub file.
epub_exclude_files = ['search.html']

# -- Extension configuration -------------------------------------------------

# -- Options for autodoc extension -------------------------------------------

# This value selects if automatically documented members are sorted 
# alphabetical (value 'alphabetical'), by member type (value 'groupwise') 
# or by source order (value 'bysource'). The default is alphabetical.
autodoc_member_order = 'bysource'

# This value is a list of autodoc directive flags that should be automatically
# applied to all autodoc directives.
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# This value controls how to represent typehints.
autodoc_typehints = 'description'

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = False

# -- Options for intersphinx extension ---------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'django': ('https://docs.djangoproject.com/en/stable/', None),
    'fastapi': ('https://fastapi.tiangolo.com/', None),
    'sqlalchemy': ('https://docs.sqlalchemy.org/en/20/', None),
    'pydantic': ('https://docs.pydantic.dev/', None),
    'click': ('https://click.palletsprojects.com/en/8.0.x/', None),
}

# -- Options for napoleon extension ------------------------------------------

# Enable parsing of NumPy and Google style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# -- Options for nbsphinx extension ------------------------------------------

# This is processed by Jinja2 and inserted before each notebook
nbsphinx_prolog = """
{% set docname = 'notebooks/' + env.doc2path(env.docname, base=None) %}

.. only:: html

    .. role:: raw-html(raw)
        :format: html

    .. nbinfo::
        :raw-html:`<a href="https://mybinder.org/v2/gh/python-mastery-hub/python-mastery-hub/main?filepath={{ docname }}" target="_blank"><img alt="Binder badge" src="https://mybinder.org/badge_logo.svg" style="vertical-align:text-bottom"></a>`

    __ https://github.com/python-mastery-hub/python-mastery-hub/blob/main/{{ docname }}
"""

# This is processed by Jinja2 and inserted after each notebook
nbsphinx_epilog = """
{% set docname = 'notebooks/' + env.doc2path(env.docname, base=None) %}

.. only:: html

    .. raw:: html

        <p><a href="https://github.com/python-mastery-hub/python-mastery-hub/blob/main/{{ docname }}" target="_blank">Download this notebook from GitHub</a>.</p>
"""

# Execute notebooks before conversion
nbsphinx_execute = 'never'

# Allow errors in notebook execution
nbsphinx_allow_errors = True

# Timeout for notebook execution (in seconds)
nbsphinx_timeout = 60

# -- Options for copybutton extension ----------------------------------------

# Copy button configuration
copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True
copybutton_only_copy_prompt_lines = True
copybutton_remove_prompts = True

# -- Options for myst-parser extension ---------------------------------------

# MyST configuration
myst_enable_extensions = [
    "amsmath",
    "colon_fence",
    "deflist",
    "dollarmath",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "substitution",
    "tasklist",
]

# -- Custom CSS and JS -------------------------------------------------------

def setup(app):
    """Custom setup function for Sphinx."""
    app.add_css_file('custom.css')
    app.add_js_file('custom.js')