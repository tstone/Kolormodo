#!/usr/bin/env python
from advertising import content
import random
import logging

def generate_ad(lang):
    # Do some magic

    section = 'generic'

    adv = __import__('advertising.content.%s' % section)
    con = getattr(adv, 'content')
    sec = getattr(con, section)
    ads = getattr(sec, 'ADS')
    return random.choice(ads)