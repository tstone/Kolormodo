#!/usr/bin/env python
from google.appengine.ext import db

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