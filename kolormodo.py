#!/usr/bin/env python
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template as webapp_template
from decorators import authenticated
from data import DataLayer
from urllib import unquote
import os.path
import logging

datalayer = DataLayer()

class BaseHandler(webapp.RequestHandler):
    def __init__(self, *args, **kwargs):
        self.data = datalayer
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
        self.render_return(template='home.html')

class BrowseHandler(BaseHandler):
    def get(self):
        self.render_return(template='home.html')

class CreateHandler(BaseHandler):
    def get(self):
        self.render_return(template='home.html')

class ShareHandler(BaseHandler):
    @authenticated
    def get(self):
        self.render_return(template='share.html')

class ShareUploadHandler(BaseHandler):
    def post(self):
        #f = self.request.files[key][0]
        #self.data.new_colorscheme(data=f['body'], filename=f['filename'], user=users.get_current_user())

        filename = str(self.request.get('qqfile'))
        data = unquote(self.request.body).replace('+', ' ')
        self.data.new_colorscheme(data=data, user=users.get_current_user())
        self.response.out.write('{"success":true}')

        """
        try:
            self.data.new_colorscheme(data=data, user=users.get_current_user())
            self.response.out.write('{"success":true}')
        except:
            self.response.out.write('{"success":false}')"""

# --- Application ---
application = webapp.WSGIApplication(
    [
        ('/share/upload', ShareUploadHandler),
        ('/share', ShareHandler),
        ('/create', CreateHandler),
        ('/browse', BrowseHandler),
        ('/', HomeHandler),
    ],
    debug=True
)
if __name__ == '__main__':
    run_wsgi_app(application)