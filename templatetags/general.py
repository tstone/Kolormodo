#!/usr/bin/env python

from google.appengine.ext.webapp import template
register = template.create_template_register()

def scheme_viewer(scheme):
    return "scheme: %s" % scheme
register.filter("scheme_viewer", scheme_viewer)