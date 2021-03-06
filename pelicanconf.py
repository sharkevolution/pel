AUTHOR = 'Sitala'
SITENAME = 'The Precognition'

PATH = 'content'

TIMEZONE = 'Europe/Kiev'

DEFAULT_LANG = 'ru'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

THEME = 'alchemy'

# Social widget
SOCIAL = (
        ('Twitter', 'http://twitter.com/shangsunset'),
        ('fa-rss', 'http://github.com/shangsunset'),
          )

DEFAULT_PAGINATION = 4

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

ICONS = (
    ('fab fa-github', 'https://github.com/sharkevolution'),
)

LINKS = (
    ('Articles', '/category/articles.html'),
    ('Misc', '/category/misc.html'),
    ('About', '/category/about.html'),
)

SITESUBTITLE = 'A magical \u2728 Pelican theme'
SITEIMAGE = '/images/1087sm-700x700.jpg'
PYGMENTS_STYLE = 'algol'
THEME_JS_OVERRIDES = ['theme/js/bootstrap.min.js',]
BOOTSTRAP_CSS = 'theme/css/bootstrap.min.css'


PLUGINS = ['plugins.bootstrap', 'render_math']

BOOTSTRAPIFY = {
    'table': ['table', 'table-striped', 'table-hover'],
    'img': ['img-fluid'],
    'blockquote': ['blockquote'],
}
# {: .img-fluid}
