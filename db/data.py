#!/usr/bin/env python

from google.appengine.ext import db
from db.models import *
from lib.ksf import KSFProcessor, KSFColor
import helpers
import logging

class DataLayer(object):
    """A singleton object for accessing the data layer"""

    def paginate(self, data_count, count, offset):
        # Limit max maginated results returned:
        p = {}
        p['total'] = int(data_count)
        p['page_count'] = (p['total'] / count) + 1
        p['current_page'] = (p['total'] - (p['total'] - offset)) / count
        p['prev_page'] = p['current_page'] - 1

        p['next_page'] = p['current_page'] + 1
        if p['next_page'] > (p['page_count'] - 1):
            p['next_page'] = 0
        logging.info(p)
        return p

    def new_colorscheme(self, filename=None, data=None, user=None):
        """Create a new ColorScheme record based on KSF data"""
        ksf = KSFProcessor(ksf_data=data)
        title = filename[0:len(filename)-4].replace('<','').replace('>','')        # Drop .ksf from the end
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
            prop = helpers.property_safe_name(lang)
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
                    setattr(cs, key, helpers.htmlencode(value))
                except:
                    pass
            cs.put()

    def get_colorschemes(self, count, offset, sort):
        schemes = ColorScheme.all().order(sort).fetch(count, offset)
        total = ColorScheme.all().order(sort).count(200)
        pagination = self.paginate(total, count, offset)
        return (schemes, pagination)

    def get_schemes_by_user(self, user, count, sort='-view_count'):
        logging.info(user)
        return ColorScheme.all().filter('author = ', user).fetch(count, 0)

    def get_scheme(self, id):
        return ColorScheme.get_by_id(int(id))

    def is_favorite(self, scheme, user):
        """Returns a datetime of when the user added as favorite or None if they haven't"""
        f = Favorite.all().filter('user = ', user).filter('scheme = ', scheme).get()
        if f:
            return f.date
        else:
            return None

    def make_favorite(self, scheme, user):
        f = Favorite(scheme = scheme, user = user)
        f.put()

    def undo_favorite(self, scheme, user):
        f = Favorite.all().filter('user = ', user).filter('scheme = ', scheme).get()
        f.delete()

    def vote_for_scheme(self, scheme, user):
        v = SchemeVotes.all().filter('user = ', user).filter('scheme = ', scheme).get()
        if v:
            return False
        else:
            v = SchemeVotes(scheme = scheme, user = user)
            v.put()
            scheme.increment_votes()
            return True

    def get_user_details(self, user):
        ud = UserDetails.all().filter('user = ', user).get()
        if not ud:
            ud = UserDetails(user=user, preferred_lang='python')    # Everybody loves Python!
            ud.save()
        return ud

    def set_user_lang(self, user, lang):
        ud = self.get_user_details(user)
        ud.preferred_lang = lang
        ud.save()
