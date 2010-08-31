#!/usr/bin/env python

import os.path
import logging
import sys
import tornado.web
import tornado.wsgi
import wsgiref.handlers
import uimodules
import socket

from google.appengine.api import users
from decorators import authenticated, administrator
from db.data import DataLayer

class BaseHandler(tornado.web.RequestHandler):
    data = DataLayer()

    """Implements Google Accounts authentication methods."""
    def get_current_user(self):
        user = users.get_current_user()
        if user:
            user.administrator = users.is_current_user_admin()
        return user

    def get_login_url(self):
        return users.create_login_url(self.request.uri)

    def render_string(self, template_name, **kwargs):
        # Let the templates access the users module to generate login URLs
        values = {
            'users': users,
            'user': self.current_user,
            'localhost': (self.request.host == 'localhost'),
            'url': self.request.uri,
            'querystring': self.request.arguments,
        }
        return tornado.web.RequestHandler.render_string(self, template_name, **dict(values,**kwargs))

    def get_lang_template_path(self, lang):
        authorized_langs = [
            'python',
            'cpp',
            'perl',
            'ruby',
            'css',
            'php',
            'xml',
        ]
        lang = lang.lower()
        if lang in authorized_langs:
            return os.path.join(os.path.dirname(__file__), "lang-snippets/", '%s.html' % lang)
        else:
            return ''

    def get_lang_template(self, lang):
        path = self.get_lang_template_path(lang)
        if path:
            f = open(path)
            html = f.read()
            f.close()
            return html
        else:
            return ''


class HomeHandler(BaseHandler):
    def get(self):
        values = { }

        sort = self.get_argument('s', '').lower()
        values['sort'] = sort
        if sort == 'views':
            sort = '-view_count'
        elif sort == 'downloads':
            sort = '-download_count'
        elif sort == 'votes':
            sort = '-votes'
        elif sort == 'newest':
            sort = '-published'
        else:
            sort = '-published'

        page = 0
        try:
            page = int(self.get_argument('p', '1')) - 1
        except:
            pass

        per_page = 10
        offset = page * per_page
        schemes,pagination = self.data.get_colorschemes(per_page, offset, sort)

        values['schemes'] = schemes
        values['pagination'] = pagination

        lang = self.get_argument('lang', None)
        if not lang:
            ud = self.data.get_user_details(self.current_user)
            if ud.preferred_lang:
                lang = ud.preferred_lang
            else:
                lang = 'python'
        values['lang'] = lang

        self.render('home.html', **values)


class SchemeHandler(BaseHandler):
    def get(self, *args):
        scheme_id = args[0]
        scheme = self.data.get_scheme(scheme_id)
        if scheme:
            newargs = list(args)
            newargs[0] = scheme
            self.get_with_scheme(*newargs)
        else:
            raise tornado.web.HTTPError(404)

    def get_with_scheme(self, scheme):
        """Override to implement"""
        pass


class AuthSchemeHandler(BaseHandler):
    @authenticated
    def get(self, *args):
        scheme_id = args[0]
        scheme = self.data.get_scheme(scheme_id)
        if scheme:
            newargs = list(args)
            newargs[0] = scheme
            self.get_with_scheme(*newargs)
        else:
            raise tornado.web.HTTPError(404)

class SchemeActionHandler(AuthSchemeHandler):
    def action(self, *args):
        """Override to implement"""
        pass
    def get_with_scheme(self, *args):
        if self.action(*args):
            if 'X-Requested-With' in self.request.headers and self.request.headers['X-Requested-With'] =='XMLHttpRequest':
                self.write('')
            else:
                if 'Referer' in self.request.headers:
                    self.redirect(self.request.headers['Referer'])
                else:
                    self.redirect('/')

class AuthActionHandler(BaseHandler):
    @authenticated
    def get(self, *args):
        if self.action(*args):
            if 'X-Requested-With' in self.request.headers and self.request.headers['X-Requested-With'] =='XMLHttpRequest':
                self.write('')
            else:
                if 'Referer' in self.request.headers:
                    self.redirect(self.request.headers['Referer'])
                else:
                    self.redirect('/')


class DownloadHandler(SchemeHandler):
    def get_with_scheme(self, scheme, slug=None):
        scheme.increment_downloads()
        self.set_header('Content-Type', 'application/ksf')
        self.write(scheme.raw)


class PreviewHandler(SchemeHandler):
    def get_with_scheme(self, scheme, slug=None):
        scheme.increment_views()
        values = {
            'scheme': scheme,
        }

        values['lang'] = self.get_argument('lang', None)
        logging.info('lang: %s' % values['lang'])
        if not values['lang']:
            ud = self.data.get_user_details(self.current_user)
            if ud.preferred_lang:
                values['lang'] = ud.preferred_lang
            else:
                values['lang'] = 'python'
        logging.info('lang: %s' % values['lang'])

        values['lang_template'] = self.get_lang_template(values['lang'])

        if 'Referer' in self.request.headers:
            values['back'] = self.request.headers['Referer']
        else:
            values['back'] = '/'

        if self.current_user:
            values['user_favorite'] = self.data.is_favorite(scheme, self.current_user)
        else:
            values['user_favorite'] = None
            values['login_url'] = self.get_login_url()

        return self.render('preview.html', **values)


class FavoriteHandler(SchemeActionHandler):
    def action(self, scheme, action):
        if action == 'add':
            self.data.make_favorite(scheme, self.current_user)
        elif action == 'undo':
            self.data.undo_favorite(scheme, self.current_user)
        else:
            # Not Implemented
            raise tornado.web.HTTPError(405)
        return True


class VoteHandler(SchemeActionHandler):
    def action(self, scheme):
        voted = self.data.vote_for_scheme(scheme, self.current_user)
        if not voted:
            raise tornado.web.HTTPError(403)
            return False
        return True


class UserSetLangHandler(AuthActionHandler):
    @authenticated
    def action(self):
        self.data.set_user_lang(self.current_user, self.get_argument('lang', 'python'))
        return True



class ApiGetTemplateHandler(BaseHandler):
    def get(self):
        template = self.get_lang_template(self.get_argument('lang', ''))
        if template:
            return self.write(template)
        else:
            raise tornado.web.HTTPError(404)


# ----------------------------------------------------------------------------------------------------------
#  Applicaiton Initialization
# ----------------------------------------------------------------------------------------------------------
if __name__ == "__main__":

    # Routes
    routes = [
        #(r"/entry/([^/]+)", EntryHandler),
        (r"/", HomeHandler),
        (r"/scheme/preview/(\d+)", PreviewHandler),
        (r"/scheme/preview/(\d+)/([^/]+)", PreviewHandler),
        (r"/scheme/download/(\d+)", DownloadHandler),
        (r"/scheme/download/(\d+)/([^/]+).ksf", DownloadHandler),
        (r"/scheme/favorite/(\d+)/([^/]+)", FavoriteHandler),
        (r"/scheme/vote/(\d+)", VoteHandler),
        (r"/user/set/lang", UserSetLangHandler),
        (r"/api/get-template", ApiGetTemplateHandler),
    ]

    # Settings
    settings = {
        "template_path": os.path.join(os.path.dirname(__file__), "templates"),
        "xsrf_cookies": True,
        "ui_modules": uimodules,
    }

    application = tornado.wsgi.WSGIApplication(routes, **settings)
    wsgiref.handlers.CGIHandler().run(application)