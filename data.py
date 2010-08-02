#!/usr/bin/env python

from google.appengine.ext import db
from lib.ksf import KSFProcessor, KSFColor
from re import IGNORECASE
import re

class ColorScheme(db.Model):
    author = db.UserProperty()
    title = db.StringProperty(required=True)
    slug = db.StringProperty(required=True)
    raw = db.TextProperty(required=True)
    colors = db.StringListProperty()
    extra_langs = db.StringListProperty()
    published = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)

class DataLayer(object):

    def new_colorscheme(self, filename=None, data=None, user=None):
        langs = []
        colors = []

        ksf = KSFProcessor(ksf_data=data)
        for lang,value in ksf.lang_styles.items():
            langs.append(lang)

        cs = ColorScheme(
            author = user,
            #title = re.sub('.ksf', filename, IGNORECASE),
            title = 'Uploaded scheme',
            slug = 'uploaded-scheme',
            raw = data,
            extra_langs = langs,
            colors = [],
        )
        cs.put()
