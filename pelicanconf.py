AUTHOR = 'Sitala'
SITENAME = 'The Precognition'
SITESUBTITLE = 'Личный блог Николая Ситала'

PATH = 'content'

TIMEZONE = 'Europe/Kiev'

DEFAULT_LANG = 'ru'
DEFAULT_PAGINATION = 6

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

THEME = 'alchemy'
THEME_CSS_OVERRIDES = ['theme/css/oldstyle.css']

# Social widget
# SOCIAL = (
#         ('Twitter', 'https://twitter.com/nsitala'),
#         ('fa-rss', 'https://github.com/sharkevolution'),
#           )
# https://sharkevolution.github.io/mylab/

ICONS = (
    ('fa-jupyter', 'https://mybinder.org/v2/git/https%3A%2F%2Fbitbucket.org%2Fsharkevolution%2Frequirements%2Fsrc%2Fmaster/HEAD'),
    ('fa-python', 'https://sharkevolution.github.io/mylab/'),

)

LINKS = (
    ('Articles', '/category/articles.html'),
    ('Django', '/category/django.html'),
    ('Jupyter', '/category/notebooks.html'),
    ('Algorithms', '/category/algorithms.html'),
    ('QGIS', '/category/qgis.html'),
    ('Excel', '/category/excel.html'),
    ('Science', '/category/science.html'),
    ('Misc', '/category/misc.html'),
    ('About', '/category/about.html'),
)

RFG_FAVICONS = True

# SITESUBTITLE = 'A magical \u2728 Pelican theme'
SITEIMAGE = '/images/1087sm-700x700.png width=300 height=300'

PYGMENTS_STYLE = 'autumn'

THEME_JS_OVERRIDES = ['theme/js/bootstrap.min.js',]
BOOTSTRAP_CSS = 'theme/css/bootstrap.min.css'
FONTAWESOME_CSS = 'theme/css/fork-awesome.css'

PLUGINS = ['plugins.bootstrap', 'plugins.render_math', 'plugins.tipue_search', "sitemap"]

BOOTSTRAPIFY = {
    'table': ['table', 'table-striped', 'table-hover'],
    'img': ['img-fluid', "img-thumbnail"],
    'blockquote': ['blockquote'],
}

SITEMAP = {
    "format": "xml",
    "priorities": {
        "articles": 0.5,
        "indexes": 0.5,
        "pages": 0.5
    },
    "changefreqs": {
        "articles": "monthly",
        "indexes": "daily",
        "pages": "monthly"
    }
}

# # Default value is ['index', 'tags', 'categories', 'authors', 'archives']
# DIRECT_TEMPLATES = ['index', 'tags', 'categories', 'authors', 'archives', 'sitemap']
# SITEMAP_SAVE_AS = 'sitemap.xml'

MARKDOWN = {
    "extension_configs": {
        # Needed for code syntax highlighting
        "markdown.extensions.codehilite": {"css_class": "highlight"},
        "markdown.extensions.extra": {},
        "markdown.extensions.meta": {},
        # This is for enabling the TOC generation
        "markdown.extensions.toc": {"title": "Оглавление"},
    },
    "output_format": "html5",
    'extensions': ['customblocks',],
}
