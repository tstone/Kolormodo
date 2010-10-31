#!/usr/bin/env python
from helpers import gravatar_hash
from tornado.escape import xhtml_escape
from advertising.manager import generate_ad
import os.path
import tornado.web
import logging
import urlparse

class BaseUIModule(tornado.web.UIModule):
    def __init__(self, handler):
        self.data = handler.data
        super(BaseUIModule, self).__init__(handler)

    def render_string(self, *args, **kwargs):
        return self.handler.render_string(*args, **kwargs)

    def get_login_url(self):
        return self.handler.get_login_url()


class numOrZero(BaseUIModule):
    def render(self, value):
        if not value:
            return 0
        else:
            return value


class safenum(BaseUIModule):
    def render(self, value):
        if not value:
            return 0
        else:
            try:
                value = int(value)
            except:
                return 0
            if value > 100000:
                return 'tons'
            elif value > 1000:
                value = str(value)
                return '%sk' % value[:-3]
            else:
                return value


class set_sort_url(BaseUIModule):
    def render(self, querystring, value):
        url = '?'
        for q in querystring:
            if not q == 's' and not q == 'p':
                for val in querystring[q]:
                    url += '%s=%s&' % (q, val)

        querystring['s'] = [value,]

        if len(url) > 1:
            return '%s&%s=%s' % (url[:-1], 's', value)
        else:
            return '?%s=%s' % ('s', value)


class querystring_replace(BaseUIModule):
    def render(self, querystring, name, value):
        url = '?'
        for q in querystring:
            if not q == name:
                for val in querystring[q]:
                    url += '%s=%s&' % (q, val)

        querystring[name] = [value,]

        if len(url) > 1:
            return '%s&%s=%s' % (url[:-1], name, value)
        else:
            return '?%s=%s' % (name, value)


class AdMediumSquare(BaseUIModule):
    def render(self):
        ad = generate_ad('css')
        return self.render_string('modules/ads/medium-square.html', ad=ad)


class DoubleAdMediumSquare(BaseUIModule):
    def render(self):
        ad_1 = generate_ad('')
        ad_2 = generate_ad('')
        return self.render_string('modules/ads/double-ad.html', ad_1=ad_1, ad_2=ad_2,)


class UserHeader(BaseUIModule):
    def render(self):
        if self.current_user:
            return self.render_string('modules/header-user.html', gravatar_hash=gravatar_hash(self.current_user.email()))
        else:
            return self.render_string('modules/header-user.html', login_url = self.get_login_url())


class SchemePreviewSmall(BaseUIModule):
    def render(self, scheme, lang='python'):
        template = self.handler.get_lang_template(lang)
        return self.render_string('modules/scheme-preview-small.html', scheme=scheme, lang_template=template, lang=lang)


class PaginationControls(BaseUIModule):
    def render(self, pagination):
        return self.render_string('modules/pagination-controls.html', p=pagination)

class SchemesByAuthorList(BaseUIModule):
    def render(self, user):
        schemes = self.data.get_schemes_by_user(user, 5)
        logging.info('**************************************** schemes: %s' % schemes.count(5))
        return self.render_string('modules/schemes-by-author-list.html', schemes=schemes)

class ErrorPanel(BaseUIModule):
    def render(self, error):
        return self.render_string('modules/error-panel.html', error=error)
