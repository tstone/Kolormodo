#!/usr/bin/env python

import os.path
import logging
import sys
import tornado.web
import tornado.wsgi
import wsgiref.handlers
import uimodules
import socket
import re
import urllib

from google.appengine.api import users
from google.appengine.api import urlfetch
from google.appengine.api import mail
from google.appengine.api import memcache
from decorators import authenticated, administrator
from db.data import DataLayer
from helpers import gravatar_hash

LANGS = [
    'python',
    'cpp',
    'perl',
    'ruby',
    'css',
    'php',
    'xml',
]

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

    def get_logout_url(self):
        return users.create_logout_url(self.request.uri)

    def render_string(self, template_name, **kwargs):
        # Let the templates access the users module to generate login URLs
        values = {
            'users': users,
            'user': self.current_user,
            'user_details': self.data.get_user_details(user=self.current_user),
            'localhost': (self.request.host == 'localhost:8080'),
            'url': self.request.uri,
            'querystring': self.request.arguments,
        }
        if not 'error' in values:
            values['error'] = None
        return tornado.web.RequestHandler.render_string(self, template_name, **dict(values,**kwargs))

    def get_lang_template_path(self, lang):
        lang = lang.lower()
        if lang in LANGS:
            return os.path.join(os.path.dirname(__file__), "lang-snippets/", '%s.html' % lang)
        else:
            return ''

    def get_lang_template(self, lang):
        lang = lang.lower()
        if lang in LANGS:
            # Check first in cache first
            mc_key = 'lang_template_%s' % lang
            html = memcache.get(mc_key)
            if not html:
                path = self.get_lang_template_path(lang)
                if path:
                    try:
                        f = open(path)
                        html = f.read()
                        memcache.set(mc_key, html)
                        f.close()
                    except:
                        logging.error('COULD NOT LOAD LANGUAGE TEMPLATE: %s' % path)
            return html
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
        setlang = self.get_argument('lang', None)
        if setlang:
            lang = setlang
            self.data.set_user_lang(self.current_user, lang)
        else:
            if not lang:
                lang = 'python'
                if self.current_user:
                    ud = self.data.get_user_details(user=self.current_user)
                    if ud.preferred_lang:
                        lang = ud.preferred_lang
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

    def get_with_scheme(self, scheme):
        """Override to implement"""
        pass


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
        values = { 'scheme': scheme }
        values['author_details'] = self.data.get_user_details(user=scheme.author)
        values['lang'] = self.get_argument('lang', None)

        if not values['lang']:
            values['lang'] = 'python'
            if self.current_user:
                ud = self.data.get_user_details(user=self.current_user)
                if ud.preferred_lang:
                    values['lang'] = ud.preferred_lang

        values['lang_template'] = self.get_lang_template(values['lang'])

        values['back'] = self.request.headers.get('Referer', '/')
        if not re.match(r'/$|/\?', values['back']):
            values['back'] = '/'

        if self.current_user:
            values['user_favorite'] = self.data.is_favorite(scheme, self.current_user)
        else:
            values['user_favorite'] = None
            values['login_url'] = self.get_login_url()

        return self.render('preview.html', **values)


class ShareHandler(BaseHandler):
    @authenticated
    def get(self):
        return self.render('share.html', error=None)

    def post(self):
        # User must agree
        if not self.get_argument('agreement', None) == 'on':
            self.render('share.html', error='Please agree to the license before sharing that theme.')

        # Grab scheme data
        data = None
        if 'fileupload' in self.request.files:
            fileupload = self.request.files['fileupload'][0]
            data = fileupload['body']
            filename = fileupload['filename']
        else:
            directinput = self.get_argument('directinput', None)
            if directinput:
                data = directinput
            else:
                data = self.get_argument('github-gist', None)

        title = self.get_argument('title', '')
        desc = self.get_argument('desc', '')
        url = self.get_argument('gist-url', '')

        # Store in DB
        if not data:
            self.render('share.html', error='That scheme appears to be blank.  Nice one.')
        else:
            try:
                cs = self.data.new_colorscheme(data=data, user=self.current_user, title=title, description=desc, url=url)
                self.data.clear_colorscheme_cache()
                self.redirect('/?s=new')
                #self.redirect(cs.edit_url)
            except:
                # Record the failure in case it was a valid file
                logging.error(data)
                self.render('share.html', error='<p>The uploaded scheme does not appear to be a valid Komodo Color Scheme -OR- it is a newer version scheme file than is currently supported.</p><p>A raw copy of your color scheme has been recorded so that we can improve our upload process.</p>')


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


class EditSchemeHandler(AuthSchemeHandler):
    def get_with_scheme(self, scheme):
        # Make sure this user owns this scheme
        if not scheme.author == self.get_current_user():
            self.redirect('/')
        self.render('edit.html', scheme=scheme)


class UserSetLangHandler(AuthActionHandler):
    @authenticated
    def action(self):
        lang = self.get_argument('lang', 'python')
        self.data.set_user_lang(self.current_user, lang)
        return True


class ApiGetTemplateHandler(BaseHandler):
    def get(self):
        template = self.get_lang_template(self.get_argument('lang', ''))
        if template:
            return self.write(template)
        else:
            raise tornado.web.HTTPError(404)


class StaticInfoHandler(BaseHandler):
    def get(self, page):
        if page == 'about':
            self.render('info/about.html')
        elif page == 'blog':
            self.render('info/blog.html')
        elif page == 'contact':
            self.render('info/contact.html')
        else:
            self.render('info/about.html')


class GetGistHandler(BaseHandler):
    def get(self, id, filename):
        try:
            url = 'http://gist.github.com/raw/%s/%s' % (id, urllib.quote(filename))
            resp = urlfetch.fetch(url)
            if resp:
                self.finish(resp.content)
            else:
                self.finish('')
        except:
            self.finish('')


class UserAccountHandler(BaseHandler):
    @authenticated
    def get(self):
        values = {
            'gravatar_hash': gravatar_hash(self.current_user.email()),
            'user_details': self.data.get_user_details(user=self.current_user)
        }
        return self.render('account.html', **values)

    @authenticated
    def post(self):
        # Figure out which we're doing, profile or settings
        nickname = self.get_argument('nickname', None)
        if nickname:
            values = {
                'nickname': nickname,
                'email': self.get_argument('email', None),
                'website': self.get_argument('website', None),
                'bio': self.get_argument('bio', None),
                'github_name': self.get_argument('github-name', None),
                'stackoverflow_name': self.get_argument('stackoverflow-name', None),
                'twitter': self.get_argument('twitter', None),
            }
        self.data.update_user_details(self.current_user, values)
        return self.redirect('/')


class UserProfileHandler(BaseHandler):
    def get(self, uid):
        ud = self.data.get_user_details(uid=uid)
        if ud:
            values = {
                'gravatar_hash': gravatar_hash(ud.safe_email),
                'user_details': ud
            }
            return self.render('user.html', **values)
        else:
            raise tornado.web.HTTPError(404)


class GoogleWebmasterConfirmation(tornado.web.RequestHandler):
    def get(self):
        self.finish('google-site-verification: google7af070066b359388.html')

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
        (r"/scheme/edit/(\d+)", EditSchemeHandler),
        (r"/share", ShareHandler),
        (r"/github/get-gist/(\d+)/([^/]+)", GetGistHandler),
        (r"/user/set/lang", UserSetLangHandler),
        (r"/user/account", UserAccountHandler),
        (r"/user/(\d+)", UserProfileHandler),
        (r"/api/get-template", ApiGetTemplateHandler),
        (r"/info/?(.*)", StaticInfoHandler),
        (r"/google7af070066b359388.html", GoogleWebmasterConfirmation),
    ]

    # Settings
    settings = {
        "template_path": os.path.join(os.path.dirname(__file__), "templates"),
        "xsrf_cookies": True,
        "ui_modules": uimodules,
    }

    memcache.flush_all()
    application = tornado.wsgi.WSGIApplication(routes, **settings)
    wsgiref.handlers.CGIHandler().run(application)