import urllib
import md5
from re import IGNORECASE
import re

def slugify(input):
    return urllib.urlencode(input.replace(' ', '-').lower())

def gravatar_hash(email):
    return md5.new(email.lower()).hexdigest()
