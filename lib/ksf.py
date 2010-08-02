from demjson import JSON
from re import DOTALL
import re

class KSFColor(object):
    """A class for understanding and manipulating KSF color values"""

    def __init__(self, ksf_color_value=None):
        self.hex = None
        self.r = None
        self.g = None
        self.b = None

        if ksf_color_value:
            self.load_ksf_color_value(ksf_color_value)

    def load_ksf_color_value(self, value):
        # KSF color value is BGR hex represented as a base 10 integer
        h = '%x' % value
        while len(h) < 6:
            h += '0'

        #print '%s => %s' % (value, h)
        self.b = int(h[0:1], 16)
        self.g = int(h[2:3], 16)
        self.r = int(h[4:5], 16)
        self.hex = '%s%s%s' % (
            h[4:5],
            h[2:3],
            h[0:1],
        )

    def get_rgb(self, default=None):
        if not self.r or not self.g or not self.b:
            return default
        return (self.r, self.g, self.b)

    def get_bgr(self, default=None):
        if not self.r or not self.g or not self.b:
            return default
        return (self.b, self.g, self.r)

    def get_html_hex(self, default=None):
        if not self.hex:
            return default
        return '#%s' % self.hex

    def set(self, rgb=None, html_hex=None, bgr_dec=None):
        if rgb:
            # TODO
            pass

        elif html_hex:
            # TODO
            pass

        elif bgr_dec:
            self.load_ksf_color_value(bgr_dec)

class KSFProcessor(object):
    """A class to process and understand KSF komodo scheme files"""

    def __init__(self, ksf_data=None, ksf_file=None, parse_colors=True):
        self.version = 4
        self.booleans = {}
        self.common_styles = {}
        self.lang_styles = {}
        self.misc_lang_settings = {}
        self.colors = {}
        self.indicators = {}
        self.parse_colors = parse_colors
        self._all_colors = []

        if ksf_data:
            self.load_data(ksf_data)
        elif ksf_file:
            self.load_file(ksf_file)

    def load_data(self, data):
        """Load raw string KSF data into an object"""
        # Detect version
        m = re.search('Version(?: )?=(?: )?([456])', data)
        if (m):
            self.version = int(m.group(1))
            data = data.replace(m.group(0), '').strip()

            # Parse accordingly...
            if self.version == 4:
                self._parse_version4(data)
        else:
            raise Exception("Could not find version in KSF data.")

    def load_file(self, file):
        """Load a KSF file into an object"""
        f = open(file, "r")
        data = f.read()
        f.close()
        self.load_data(data)

    def get_all_colors(self, format='html_hex'):
        """ Returns an array of all the colors in the scheme. Possible formats:  html_hex, rgb, bgr"""
        allcolors = []
        for color in self._all_colors:
            if format == 'html_hex':
                c = color.get_html_hex()
            elif format == 'rgb':
                c = color.get_rgb()
            elif format == 'bgr':
                c = color.get_bgr()
            # Append if value and not already present
            if c and not c in allcolors:
                allcolors.append(c)
        return allcolors

    def _load_child_color(self, iter, parent_key, child_key):
        if child_key in iter[parent_key]:
            if iter[parent_key][child_key] == 'None': return None
            iter[parent_key][child_key] = KSFColor(iter[parent_key][child_key])
            self._all_colors.append(iter[parent_key][child_key])

    def _parse_version4(self, ksf_data):
        # Enumerate sections
        for section in ksf_data.split('\n\n'):
            m = re.search('([\w]+)(?: )?=(?: )?(.+)', section, DOTALL)
            if m:
                # Format data strings
                raw = m.group(2).strip()
                raw = raw.replace('True', "'True'").replace('False', "'False'")
                raw = raw.replace('None', "''")

                section = m.group(1)
                json = JSON(strict=False)
                data = json.decode(raw)

                if section == 'Booleans':
                    self.booleans = data
                    # Make sure all values are True/False
                    for key,value in self.booleans.items():
                        if str(value) == 1 or value == 'True':
                            self.booleans[key] = True
                        elif str(value) == 0 or value == 'False':
                            self.booleans[key] = False

                elif section == 'CommonStyles':
                    self.common_styles = data
                    if self.parse_colors:
                        for key,value in self.common_styles.items():
                            self._load_child_color(self.common_styles, key, 'fore')
                            self._load_child_color(self.common_styles, key, 'back')

                elif section == 'LanguageStyles':
                    self.lang_styles = data
                    if self.parse_colors:
                        for key,value in self.lang_styles.items():
                            for lang_key,lang_value in self.lang_styles[key].items():
                                self._load_child_color(self.lang_styles[key], lang_key, 'fore')
                                self._load_child_color(self.lang_styles[key], lang_key, 'back')

                elif section == 'MiscLanguageSettings':
                    self.misc_lang_settings = data

                elif section == 'Colors':
                    self.colors = data
                    if self.parse_colors:
                        for key,value in self.colors.items():
                            self.colors[key] = KSFColor(self.colors[key])
                            self._all_colors.append(self.colors[key])

                elif section == 'Indicators':
                    self.indicators = data
                    if self.parse_colors:
                        for key,value in self.indicators.items():
                            self._load_child_color(self.indicators, key, 'fore')
                            self._load_child_color(self.indicators, key, 'back')

    def build_css(self, language=None, class_prefix=''):
        css = ''

        if class_prefix:
            class_prefix += ' '     # Add space for proper CSS

        def formatStyle(iter, key, css_attr):
            iscolor = (css_attr == 'color' or css_attr == 'background-color')

            if key in iter:
                if iscolor:
                    if hasattr(iter[key], 'get_html_hex'):
                        return '%s: %s; ' % (css_attr, iter[key].get_html_hex())
                elif css_attr == 'font-weight':
                    val = str(iter[key])
                    if val == '1' or val == 'True':
                        return 'font-weight: bold;'
                    else:
                        return 'font-weight: normal;'
                elif css_attr == 'font-style':
                    val = str(iter[key])
                    if val == '1' or val == 'True':
                        return 'font-style: italic;'
                    else:
                        return 'font-style: normal;'
                elif css_attr == 'font-size':
                    fs = int(iter[key]) + 3
                    return '%s: %spx; ' %(css_attr, fs)
                elif css_attr == 'font-family':
                    if ' ' in iter[key]:
                        return '%s: "%s", monospace; ' %(css_attr, iter[key])
                    else:
                        return '%s: %s, monospace; ' %(css_attr, iter[key])
                else:
                    return '%s: %s; ' %(css_attr, iter[key])
            return ''

        styles = self.common_styles
        if language:
            if not language in self.lang_styles:
                raise Exception('%s Language not found in language-specific styles.' % language)
            lang_styles = self.lang_styles[language]
            for key,value in lang_styles.items():
                styles[key] = value

        if styles:
            for style,style_value in styles.items():
                s = ''
                if hasattr(styles[style], '__iter__'):
                    for prop, prop_value in styles[style].items():
                        if prop == 'fore':
                            s += formatStyle(styles[style], prop, 'color')
                        elif prop == 'back':
                            s += formatStyle(styles[style], prop, 'background-color')
                        elif prop == 'bold':
                            s += formatStyle(styles[style], prop, 'font-weight')
                        elif prop == 'italic':
                            s += formatStyle(styles[style], prop, 'font-style')
                        elif prop == 'face':
                            s += formatStyle(styles[style], prop, 'font-family')
                        elif prop == 'size':
                            s += formatStyle(styles[style], prop, 'font-size')

                if s:
                    css += '%s.ksf-%s { %s}\n' % (
                        class_prefix,
                        style.replace('-', ' '),
                        s
                    )

        # Configure default parent style
        if self.booleans.get('preferFixed', True):
            css = css.replace('.ksf-default_fixed', '.ksf-common')
        else:
            css = css.replace('.ksf-default_proportional', '.ksf-common')

        # Toggle-on features
        if self.booleans.get('caretLineVisible', False):
            if 'caretLineBack' in self.colors:
                if hasattr(self.colors['caretLineBack'], 'get_html_hex'):
                    css += '%s.ksf-line-highlight { background-color: %s }\n' % (class_prefix, self.colors['caretLineBack'].get_html_hex())

        if 'selBack' in self.colors:
            s = ''
            if hasattr(self.colors['selBack'], 'get_html_hex'):
                s += 'background-color:%s; ' % self.colors['selBack'].get_html_hex()
            if self.booleans.get('useSelFore', False):
                if 'selFore' in self.colors:
                    if hasattr(self.colors['selFore'], 'get_html_hex'):
                        s += 'color:%s; ' % self.colors['selFore'].get_html_hex()

                        # Build a cascading list of classes to make sure we override them all
                        foreOverride = ''
                        for key,value in styles.items():
                            foreOverride += '%s.ksf-selected .ksf-%s,\n' % (class_prefix, key)
                        css += '%s { color: %s }\n' % ( foreOverride[:-2], self.colors['selFore'].get_html_hex() )

            css += '%s.ksf-selected { %s}\n' % (class_prefix, s)

        return css