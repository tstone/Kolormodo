#!/usr/bin/env python
from google.appengine.ext import db
from urllib import quote
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
    favorite_count = db.IntegerProperty()
    votes = db.IntegerProperty()

    @property
    def safe_id(self):
        return self.key().id()

    @property
    def slug(self):
        return helpers.property_safe_name(self.title)

    @property
    def download_url(self):
        return '/scheme/download/%s/%s.ksf' % (self.safe_id, quote(self.slug))

    @property
    def preview_url(self):
        return '/scheme/preview/%s/%s' % (self.safe_id, quote(self.slug))

    @property
    def favorite_url(self):
        return '/scheme/favorite/%s' % self.safe_id

    @property
    def vote_url(self):
        return '/scheme/vote/%s' % self.safe_id

    @property
    def edit_url(self):
        return '/scheme/edit/%s' % self.safe_id

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
        try:
            if self.view_count:
                self.view_count += 1
            else:
                self.view_count = 1
        except:
            self.view_count = 1
        self.save()

    def increment_downloads(self):
        # Google analytics?
        try:
            if self.download_count:
                self.download_count += 1
            else:
                self.download_count = 1
        except:
            self.download_count = 1
        self.save()

    def increment_votes(self):
        # Google analytics?
        try:
            if self.votes:
                self.votes += 1
            else:
                self.votes = 1
        except:
            self.votes = 1
        self.save()


class Favorite(db.Model):
    user = db.UserProperty()
    scheme = db.ReferenceProperty(ColorScheme)
    date = db.DateTimeProperty(auto_now_add=True)

class SchemeVotes(db.Model):
    user = db.UserProperty()
    scheme = db.ReferenceProperty(ColorScheme)
    date = db.DateTimeProperty(auto_now_add=True)

class UserDetails(db.Model):
    user = db.UserProperty()
    preferred_lang = db.StringProperty()

    @property
    def id(self):
        return self.key().id()
