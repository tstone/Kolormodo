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
import demjson as json

DATALAYER = DataLayer()
webapp_template.register_template_library('tempaltetags.general')

class BaseHandler(webapp.RequestHandler):
    def __init__(self, *args, **kwargs):
        self.data = DATALAYER
        super(BaseHandler, self).__init__(*args, **kwargs)

    def get_current_user(self):
        user = users.get_current_user()
        if user: user.administrator = users.is_current_user_admin()
        return user

    def get_login_url(self):
        return users.create_login_url(self.request.uri)

    def render_string(self, template=None, values={}):
        """Render a given template to a string"""
        path = os.path.join(os.path.dirname(__file__), 'templates/%s' % template)
        return webapp_template.render(path, values)

    def render_return(self, template=None, values={}):
        """Render the template and return as the respone"""
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write(self.render_string(template=template, values=values))


class HomeHandler(BaseHandler):
    def get(self):
        schemes = self.data.get_latest_colorschemes()
        self.render_return(template='home.html', values={ 'themes':schemes })


class BrowseHandler(BaseHandler):
    def get(self):
        self.render_return(template='browse.html')


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
        self.response.headers['Content-Type'] = 'application/json'

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
        self.response.out.write(json.encode(resp))
        #except:
        #    self.response.out.write(json.encode({ 'succes':False }))



ROUTES = [
    ('/share/upload', ShareUploadHandler),
    ('/share/save', ShareSaveHandler),
    ('/share', ShareHandler),
    ('/create', CreateHandler),
    ('/browse', BrowseHandler),
    ('/', HomeHandler),
]

# Import custom django libraries
#webapp.template.register_template_library('utils.django_libs.gravatar')

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    logging.debug('Starting webapp...')
    application = webapp.WSGIApplication(ROUTES, debug=True)
    run_wsgi_app(application)
