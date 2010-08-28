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
            'localhost': (self.request.host == 'localhost')
        }
        return tornado.web.RequestHandler.render_string(self, template_name, **dict(values,**kwargs))

    def get_lang_template_path(self, lang):
        authorized_langs = [
            'python',
            'cpp',
            'perl',
            'ruby',
            'css'
        ]
        lang = lang.lower()
        if lang in authorized_langs:
            return os.path.join(os.path.dirname(__file__), "templates/lang-snippets/", '%s.html' % lang)
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
        sort = self.get_argument('s', '').lower()
        if sort == 'views':
            sort = 'view_count'
        elif sort == 'downloads':
            sort = 'download_count'
        elif sort == 'votes':
            sort = 'votes'
        elif sort == 'newest':
            sort = '-published'
        else:
            sort = '-published'

        schemes = self.data.get_colorschemes(12, 0, sort)
        self.render('home.html', schemes=schemes)

class DownloadHandler(BaseHandler):
    def get(self, scheme_id, slug=None):
        scheme = self.data.get_scheme(scheme_id)
        if scheme:
            scheme.increment_downloads()
            self.set_header('Content-Type', 'application/ksf')
            self.write(scheme.raw)
        else:
            raise tornado.web.HTTPError(404)

class PreviewHandler(BaseHandler):
    def get(self, scheme_id, slug=None):
        scheme = self.data.get_scheme(scheme_id)
        if scheme:
            scheme.increment_views()
            template = self.get_lang_template('python')
            return self.render('preview.html', scheme=scheme, lang_template=template)
        else:
            raise tornado.web.HTTPError(404)


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
        (r"/preview/(\d+)", PreviewHandler),
        (r"/preview/(\d+)/([^/]+)", PreviewHandler),
        (r"/download/(\d+)", DownloadHandler),
        (r"/download/(\d+)/([^/]+).ksf", DownloadHandler),
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