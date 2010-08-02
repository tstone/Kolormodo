#!/usr/bin/env python

from google.appengine.ext import db
from lib.ksf import KSFProcessor, KSFColor

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
    def slugify(self, input):
        return input.replace(' ', '-').lower()

    def new_colorscheme(self, filename=None, data=None, user=None):
        """Create a new ColorScheme record based on KSF data"""
        ksf = KSFProcessor(ksf_data=data)
        title = filename[0:len(filename)-4]     # Drop .ksf from the end
        langs = [lang for lang,value in ksf.lang_styles.items()]

        cs = ColorScheme(
            author = user,
            title = title,
            slug = self.slugify(title),
            raw = data,
            extra_langs = langs,
            colors = ksf.get_all_colors(),
        )
        cs.put()
        return cs
