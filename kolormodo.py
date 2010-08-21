#!/usr/bin/env python
import os.path
import logging
import sys

APP_ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, APP_ROOT_DIR)
sys.path.insert(0, os.path.join(APP_ROOT_DIR, 'lib'))

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template as webapp_template
from decorators import authenticated
from db.data import DataLayer
from urllib import unquote
import helpers
import demjson as json
import logging
import db.helpers

DATALAYER = DataLayer()
#webapp_template.register_template_library('tempaltetags.general')

class BaseHandler(webapp.RequestHandler):
    def __init__(self, *args, **kwargs):
        self.data = DATALAYER
        self.template_path = os.path.join(os.path.dirname(__file__), 'templates/')
        super(BaseHandler, self).__init__(*args, **kwargs)

    def get_current_user(self):
        user = users.get_current_user()
        if user: user.administrator = users.is_current_user_admin()
        return user

    def get_login_url(self):
        return users.create_login_url(self.request.uri)

    def render_string(self, template=None, values={}):
        """Render a given template to a string"""
        path = os.path.join(self.template_path, template)
        logging.debug(path)
        return webapp_template.render(path, values)

    def render_return(self, template=None, values={}):
        """Render the template and return as the respone"""
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write(self.render_string(template=template, values=values))

    def get_lang_template(self, lang):
        # This has the looks of a bad security problem
        lang = db.helpers.property_safe_name(lang)
        f = file(os.path.join(self.template_path, 'lang-snippets/%s.html' % lang))
        template = f.read()
        f.close()
        return template


class HomeHandler(BaseHandler):
    def get(self):
        #schemes = self.data.get_latest_colorschemes(12, 0)
        self.render_return(template='home.html')


class BrowseHandler(BaseHandler):
    def get(self):
        self.render_return(template='browse.html')


class ThemeViewHandler(BaseHandler):
    def get(self, theme_id, slug=None):
        try:
            scheme = self.data.get_scheme(theme_id)

            # Check users' pref for preferred language viewing
            template = self.get_lang_template('python')

            self.render_return(template='theme.html', values={
                'page_title': '%s Color Scheme' % scheme.title,
                'scheme': scheme,
                'css': scheme.all_css(),
                'template': template,
            })
        except:
            pass

class CreateHandler(BaseHandler):
    def get(self):
        self.render_return(template='home.html')


class ShareHandler(BaseHandler):
    """UI for sharing a scheme"""
    @authenticated
    def get(self):
        self.render_return(template='share.html')


class ShareSaveHandler(BaseHandler):
    """Save the title/desc from the sharing page"""
    def post(self):
        key = self.request.get('key', None)
        title = self.request.get('title', None)
        desc = self.request.get('description', None)

        #try:
        self.data.update_colorscheme(key, **{ 'title':title, 'description':desc })
        return
        #except:
            #self.response.out.write("{ 'success':false }")


class ShareUploadHandler(BaseHandler):
    """Process incoming files destined for sharing"""
    def post(self):
        # TODO: Check for authenticated
        filename = str(self.request.get('qqfile'))
        data = unquote(self.request.body).replace('+', ' ')

        #try:
        cs = self.data.new_colorscheme(data=data, user=users.get_current_user(), filename=filename)
        resp = {
            'success':True,
            'title': cs.title,
            'colors': cs.colors,
            'background': cs.background,
            'langs': cs.extra_langs,
            'filename': filename,
            'key': str(cs.key().id()),
        }
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.encode(resp))
        #except:
        #    self.response.out.write(json.encode({ 'success':False }))


class ApiGetThemesHandler(BaseHandler):
    def get(self):
        """
        PARAMETERS:
        format = json        - Return data type (only json supported right now)
        template = lang      - Language of template to return.  Not returned if ommitted
        order =
        filter =

        RETURN:
        {
            'template': '<html> for given language,
            'schemes: [
                {
                    'title', 'css', 'desc'
                }
            ]
        }
        """

        format = self.request.get('format', 'json')
        template = self.request.get('template', None)
        resp = {}

        if template:
            resp['template'] = self.get_lang_template(template)
            resp['lang'] = template

        schemes = self.data.get_latest_colorschemes(100, 0)
        resp['schemes'] = []
        for scheme in schemes:
            resp['schemes'].append({
                'title': scheme.title,
                'desc': scheme.description,
                'css': scheme.general_css,
                'id': scheme.key().id(),
            })

        if format == 'json':
            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write(json.encode(resp))

class ApiGetTemplateHandler(BaseHandler):
    def get(self):
        """
        PARAMETERS:
        lang      - Language of template to return.  Not returned if ommitted
        """
        lang = self.request.get('lang', 'python')
        resp = {}
        resp['template'] = self.get_lang_template(lang)
        resp['lang'] =db.helpers.property_safe_name(lang)

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.encode(resp))


ROUTES = [
    ('/share/upload', ShareUploadHandler),
    ('/share/save', ShareSaveHandler),
    ('/share', ShareHandler),
    ('/create', CreateHandler),
    ('/browse', BrowseHandler),
    ('/theme/(\d+)', ThemeViewHandler),
    ('/theme/(\d+)/(.*)', ThemeViewHandler),
    ('/api/get-themes', ApiGetThemesHandler),
    ('/api/get-template', ApiGetTemplateHandler),
    ('/', HomeHandler),
]

# Import custom django libraries
#webapp.template.register_template_library('utils.django_libs.gravatar')

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    logging.debug('Starting webapp...')
    application = webapp.WSGIApplication(ROUTES, debug=True)
    run_wsgi_app(application)
