#!/usr/bin/env python

from google.appengine.ext import db
from db.models import *
from lib.ksf import KSFProcessor, KSFColor
import re


def property_safe_name(string):
    return re.sub('[^A-Za-z0-9 ]+', '', string.replace(' ','_').replace('+','plus').replace('#','sharp')).lower()

def slugify(self, input):
        return input.replace(' ', '-').lower()


class DataLayer(object):
    """A singleton object for accessing the data layer"""

    def new_colorscheme(self, filename=None, data=None, user=None):
        """Create a new ColorScheme record based on KSF data"""
        ksf = KSFProcessor(ksf_data=data)
        title = filename[0:len(filename)-4]     # Drop .ksf from the end
        langs = [lang for lang,value in ksf.lang_styles.items()]

        # Build static property values
        cs = ColorScheme(
            author = user,
            title = title,
            raw = data,
            extra_langs = langs,
            colors = ksf.get_primary_colors(),
            background = ksf.get_background_color().get_html_hex(),
            background_tone = ksf.get_background_color().get_tonality(),
        )
        # Save to generate ID
        cs.put()
        cs.general_css = ksf.build_css(css_prefix='#cs-%s' % cs.key().id(), skip_font_size=True)

        # Build dynamic property values
        for lang in langs:
            prop = property_safe_name(lang)
            value = ksf.build_css(language=lang, css_prefix='#cs-%s' % cs.key().id(), skip_font_size=True)
            setattr(cs, '%s_css' % prop, db.Text(value))
        cs.put()

        return cs

    def update_colorscheme(self, id, **kwargs):
        """Save the title and description from the share page"""
        cs = ColorScheme.get_by_id(int(id))
        if cs:
            for key,value in kwargs.items():
                try:
                    setattr(cs, key, value)
                except:
                    pass
            cs.put()

    def get_latest_colorschemes(self, count, offset):
        return ColorScheme.all().order('-published').fetch(count, offset)
