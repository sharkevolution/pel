# This file is only used if you use `make publish` or
# explicitly specify it as your config file.

import os
import sys
sys.path.append(os.curdir)
from pelicanconf import *

# If your site is available via HTTPS, make sure SITEURL begins with https://
SITEURL = 'https://sitala.netlify.app/'
RELATIVE_URLS = False

FEED_ALL_ATOM = 'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = 'feeds/{slug}.atom.xml'

DELETE_OUTPUT_DIRECTORY = True

# Following items are often useful when publishing

#DISQUS_SITENAME = ""
#GOOGLE_ANALYTICS = ""

# path-specific metadata
STATIC_PATHS = [
    'static/robots.txt',
    'images',
    ]

EXTRA_PATH_METADATA = {
    'static/robots.txt': {'path': 'robots.txt'},
    }

DISQUS_SITENAME = "sitala"
DISQUS_SECRET_KEY = 'LOu3KPyxCbyZsDbQuCZdNLyz9vCbYuNrtu3jKPDVMSw8W0xRiz6oVKD0hk2JOFNo'
DISQUS_PUBLIC_KEY = 'q3k4E3IaIFAO4RNHfnamIFd2tSbna9YfsXi6W04inKg9qWDNggS2JrSGU2Yn2W2S'

GOOGLE_ANALYTICS = "G-CEBJ98YCJW"