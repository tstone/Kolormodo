#!/usr/bin/env python
from helpers import gravatar_hash
import os.path
from tornado.escape import xhtml_escape
import tornado.web
import logging

class BaseUIModule(tornado.web.UIModule):
    def __init__(self, handler):
        self.data = handler.data
        super(BaseUIModule, self).__init__(handler)

    def render_string(self, *args, **kwargs):
        return self.handler.render_string(*args, **kwargs)

    def get_login_url(self):
        return self.handler.get_login_url()


class UserHeader(BaseUIModule):
    def render(self):
        if self.current_user:
            return self.render_string('modules/header-user.html', gravatar_hash=gravatar_hash(self.current_user.email()))
        else:
            return self.render_string('modules/header-user.html', login_url = self.get_login_url())


class SchemePreviewSmall(BaseUIModule):
    def render(self, scheme):
        template = self.handler.get_lang_template('python')
        return self.render_string('modules/scheme-preview-small.html', scheme=scheme, lang_template=template)