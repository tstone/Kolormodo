#!/usr/bin/env python
from google.appengine.ext import db
from django.template.defaultfilters import slugify
import helpers

class ColorScheme(db.Expando):
    author = db.UserProperty()
    title = db.StringProperty(required=True)
    description = db.StringProperty()
    raw = db.TextProperty(required=True)
    colors = db.StringListProperty()
    background = db.StringProperty()
    background_tone = db.IntegerProperty()
    extra_langs = db.StringListProperty()
    published = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    general_css = db.TextProperty()
    download_count = db.IntegerProperty()
    view_count = db.IntegerProperty()

    @property
    def safe_id(self):
        return self.key().id()

    @property
    def slug(self):
        return slugify(self.title)

    def all_css(self):
        css = self.general_css
        for lang in self.extra_langs:
            safe_lang = helpers.property_safe_name(lang)
            lang_css = getattr(self, '%s_css' % safe_lang, '')
            # insert lang prefix
            lang_css = lang_css.replace('.ksf-', '.%s .ksf-' % safe_lang)
            css += lang_css
        return css

    def increment_views(self):
        # Google analytics?
        if self.view_count:
            self.view_count += 1
        else:
            self.view_count = 1
        self.save()

    def increment_downloads(self):
        # Google analytics
        if self.download_count:
            self.download_count += 1
        else:
            self.download_count = 1
        self.save()
