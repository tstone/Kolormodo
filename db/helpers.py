import re

def property_safe_name(string):
    return re.sub('[^A-Za-z0-9 ]+', '', string.replace(' ','_').replace('+','p').replace('#','s')).lower()#!/usr/bin/env python

def htmlencode(string):
    if string:
        return string.replace('<','&lt;').replace('>','&gt;').replace('&','&amp;')
    else:
        return string