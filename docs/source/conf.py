from swagger_zipkin import __version__ as version


extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
]

release = version

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'swagger_zipkin'
copyright = '2016, Yelp, Inc'

exclude_patterns = []

pygments_style = 'sphinx'


# -- Options for HTML output ---------------------------------------------

html_theme = 'sphinxdoc'

html_static_path = ['_static']

htmlhelp_basename = 'swagger_zipkindoc'


intersphinx_mapping = {
    'http://docs.python.org/': None,
}
