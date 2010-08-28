#!/usr/bin/env python
from google.appengine.ext.webapp import template
import functools

def administrator(method):
    """Restrict to site admins"""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            if self.request.method == "GET":
                self.redirect(self.get_login_url())
                return
            raise tornado.web.HTTPError(403)
        elif not self.current_user.administrator:
            if self.request.method == "GET":
                self.redirect("/")
                return
            raise tornado.web.HTTPError(403)
        else:
            return method(self, *args, **kwargs)
    return wrapper

def authenticated(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.get_current_user():
            if self.request.method == "GET":
                self.redirect(self.get_login_url())
                return
        return method(self, *args, **kwargs)
    return wrapper