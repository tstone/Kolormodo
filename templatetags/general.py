#!/usr/bin/env python

from google.appengine.ext.webapp import template
from django import template as django_template

"""
def my_tag(parser, token):
    bits = list(token.split_contents())
    if len(bits) != 2:
        raise django_template.TemplateSyntaxError, "Error!!"
    return MyNode(bits[1])

class MyNode(django_template.Node):
    def __init__(self, my_var):
        self.my_var = my_var
    def render(self, context):
        try:
            my_var = django_template.resolve_variable(self.my_var, context)
        except django_template.VariableDoesNotExist:
            my_var = None
        return "my var is: %s" % my_var
"""

def my_tag(parser, token):
    bits = list(token.split_contents())
    if len(bits) != 2:
        raise django_template.TemplateSyntaxError, "Error!!"
    return MyNode(bits[1])

class MyNode(django_template.Node):
    def __init__(self, my_var):
        self.my_var = my_var
    def render(self, context):
        try:
            my_var = django_template.resolve_variable(self.my_var, context)
        except django_template.VariableDoesNotExist:
            my_var = None
        return "my var is: %s" % my_var