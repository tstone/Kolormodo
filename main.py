#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from ksf import KSFProcessor
import os


class MainHandler(webapp.RequestHandler):
    def get(self):

        data = """Version = 4

Booleans = {'caretLineVisible': True, 'preferFixed': 1, 'useSelFore': False}

CommonStyles = {'attribute name': {'fore': 7872391},
 'attribute value': {'fore': 3100463},
 'bracebad': {'back': 9117943, 'bold': 1, 'fore': 16777215},
 'bracehighlight': {'bold': 1, 'fore': 16051405},
 'classes': {'bold': True, 'fore': 9530623},
 'comments': {'fore': 10517174, 'italic': 1},
 'control characters': {'back': 0, 'fore': 16777215},
 'default_fixed': {'back': 2631720,
                   'bold': 0,
                   'eolfilled': 0,
                   'face': 'Bitstream Vera Sans Mono',
                   'fore': 16513023,
                   'hotspot': 0,
                   'italic': 0,
                   'size': 10,
                   'useFixed': 1},
 'default_proportional': {'back': 16777215,
                          'bold': 0,
                          'eolfilled': 0,
                          'face': 'Bitstream Vera Sans Mono',
                          'fore': 0,
                          'hotspot': 0,
                          'italic': 0,
                          'size': 10,
                          'useFixed': 0},
 'fold markers': {'back': 986639, 'fore': 2696233},
 'functions': {'fore': 10722047},
 'identifiers': {'fore': 14208424},
 'indent guides': {'fore': 8421504},
 'keywords': {'fore': 12887099},
 'keywords2': {'fore': 7872391},
 'linenumbers': {'back': 2631720, 'fore': 14208424},
 'numbers': {'fore': 13084888},
 'operators': {'fore': 16777215},
 'preprocessor': {'fore': 6908265},
 'regex': {'fore': 25800},
 'stderr': {'fore': 16711680, 'italic': 1},
 'stdin': {'fore': 0},
 'stdout': {'fore': 0},
 'stringeol': {'back': 10079487, 'eolfilled': 1},
 'strings': {'fore': 13084888},
 'tags': {'fore': 16724480},
 'variables': {'fore': 0}}

LanguageStyles = {'Apache': {'directives': {'fore': 9145088},
            'extensions': {'fore': 139},
            'ip_addresses': {'fore': 6908265},
            'parameters': {'fore': 7872391}},
 'C#': {'UUIDs': {'fore': 0},
        'commentdockeyword': {'fore': 0},
        'commentdockeyworderror': {'fore': 14483456},
        'globalclass': {'fore': 9145088},
        'verbatim': {'fore': 0}},
 'C++': {'UUIDs': {'fore': 0},
         'commentdockeyword': {'fore': 0},
         'commentdockeyworderror': {'fore': 14483456},
         'globalclass': {'fore': 9145088},
         'verbatim': {'fore': 0}},
 'CSS': {'classes': {'fore': 13084888},
         'compound_document_defaults': {'back': 13559807},
         'ids': {'fore': 9530623},
         'important': {'fore': 9109504},
         'tags': {'fore': 12097145},
         'values': {'fore': 15987436}},
 'Diff': {'additionline': {'fore': 9109504},
          'chunkheader': {'fore': 9145088},
          'deletionline': {'fore': 139},
          'diffline': {'fore': 6908265, 'italic': 1},
          'fileline': {'fore': 7872391, 'italic': 1}},
 'Django': {'compound_document_defaults': {'back': 14543103}},
 'Errors': {'Error lines': {'fore': 102, 'hotspot': 1, 'italic': 1}},
 'HTML': {'attribute name': {'fore': 14208424},
          'attributes': {'fore': 102},
          'cdata': {'fore': 9109504},
          'compound_document_defaults': {'back': 16772829},
          'tags': {'fore': 9530623}},
 'IDL': {'UUIDs': {'fore': 0},
         'commentdockeyword': {'fore': 0},
         'commentdockeyworderror': {'fore': 14483456},
         'globalclass': {'fore': 9145088},
         'verbatim': {'fore': 0}},
 'Java': {'UUIDs': {'fore': 0},
          'commentdockeyword': {'fore': 0},
          'commentdockeyworderror': {'fore': 14483456},
          'globalclass': {'fore': 9145088},
          'verbatim': {'fore': 0}},
 'JavaScript': {'UUIDs': {'fore': 0},
                'bracehighlight': {'fore': 16777215},
                'commentdockeyword': {'fore': 0},
                'commentdockeyworderror': {'fore': 14483456},
                'compound_document_defaults': {'back': 15138790},
                'globalclass': {'fore': 9145088},
                'identifiers': {'fore': 12097145},
                'operators': {'fore': 15987436},
                'verbatim': {'fore': 0}},
 'Mason': {'compound_document_defaults': {'back': 14544639}},
 'PHP': {'identifiers': {'fore': 10066227},
         'keywords': {'fore': 10040217},
         'operators': {'fore': 0},
         'strings': {'fore': 10040115},
         'variables': {'fore': 0}},
 'Perl': {'compound_document_defaults': {'back': 16050922},
          'here documents': {'bold': 1, 'fore': 8594211}},
 'Python': {'compound_document_defaults': {'back': 16777173},
            'decorators': {'fore': 12887099}},
 'RHTML': {'compound_document_defaults': {'back': 10092543}},
 'Regex': {'charclass': {'fore': 2237106, 'italic': 1},
           'charescape': {'fore': 9145088, 'italic': 1},
           'charset_operator': {'fore': 7872391, 'size': 12},
           'comment': {'fore': 6908265, 'italic': 1},
           'default': {},
           'eol': {},
           'groupref': {'fore': 2237106, 'italic': 1},
           'grouptag': {'fore': 7872391, 'size': 8},
           'match_highlight': {'back': 10092543},
           'operator': {'fore': 7872391, 'size': 12},
           'quantifier': {'bold': 1, 'fore': 16711680, 'size': 12},
           'special': {'bold': 1, 'fore': 16711680},
           'text': {}},
 'Ruby': {'compound_document_defaults': {'back': 15525631}},
 'Rx': {'breakpoints': {'back': 14540253},
        'children': {'back': 14540236},
        'default': {'bold': 1},
        'parents': {'back': 13434828}},
 'Smarty': {'compound_document_defaults': {'back': 10092543}},
 'Text': {},
 'XML': {'cdata': {'fore': 9109504},
         'cdata content': {'fore': 9145088},
         'cdata tags': {'fore': 9109504},
         'data': {'fore': 2302862},
         'declarations': {'fore': 3358812},
         'entity references': {'fore': 2302862},
         'pi content': {'fore': 9145088},
         'pi tags': {'fore': 9109504},
         'prolog': {'fore': 0},
         'xpath attributes': {'fore': 9109504},
         'xpath content': {'fore': 36095},
         'xpath tags': {'fore': 11}},
 'reStructuredText': {'comment': {'fore': 9616695, 'italic': 1},
                      'identifier': {'fore': 1602765},
                      'operator': {'fore': 9109504},
                      'regex': {'bold': 1}}}

MiscLanguageSettings = {'CSS': {'globalSubLanguageBackgroundEnabled': False},
 'Django': {'globalSubLanguageBackgroundEnabled': True},
 'HTML': {'globalSubLanguageBackgroundEnabled': False},
 'Mason': {'globalSubLanguageBackgroundEnabled': True},
 'Perl': {'globalSubLanguageBackgroundEnabled': True},
 'Ruby': {'globalSubLanguageBackgroundEnabled': True}}

Colors = {'bookmarkColor': 14342664,
 'callingLineColor': 10517174,
 'caretFore': 16051405,
 'caretLineBack': 3487029,
 'currentLineColor': 16764108,
 'edgeColor': 8681107,
 'foldMarginColor': 0,
 'selBack': 5394258,
 'selFore': 16772846,
 'whitespaceColor': 256}

Indicators = {'find_highlighting': {'alpha': 100,
                       'color': 14208424,
                       'draw_underneath': True,
                       'style': 7},
 'linter_error': {'alpha': 100,
                  'color': 12887099,
                  'draw_underneath': True,
                  'style': 1},
 'linter_warning': {'alpha': 100,
                    'color': 32768,
                    'draw_underneath': True,
                    'style': 1},
 'soft_characters': {'alpha': 100,
                     'color': 13084888,
                     'draw_underneath': False,
                     'style': 6},
 'tabstop_current': {'alpha': 100,
                     'color': 3355647,
                     'draw_underneath': True,
                     'style': 7},
 'tabstop_pending': {'alpha': 100,
                     'color': 16751001,
                     'draw_underneath': True,
                     'style': 6},
 'tag_matching': {'alpha': 100,
                  'color': 13084888,
                  'draw_underneath': True,
                  'style': 7}}"""
        
        ksf = KSFProcessor(ksf_data=data)
        template_values = {
            'custom_css': ksf.build_css(class_prefix='.scheme-preview')
        }
        
        path = os.path.join(os.path.dirname(__file__), 'beta.html')
        self.response.out.write(template.render(path, template_values))


def main():
    application = webapp.WSGIApplication([('/', MainHandler)], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
