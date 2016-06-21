# -*- coding:utf-8 -*-

import unittest
import xml.etree.ElementTree as ET

from statik.views import *
from statik.jinja2ext import *

from jinja2 import Environment, DictLoader

TEST_SIMPLE_VIEW = """path: /
template: home
context:
    static:
        page-title: Test page title
        other-link: http://somewhere.com
        some-html: <p><b>Hello!</b></p>
"""

TEST_TEMPLATES = {
    'home.html': """<!DOCTYPE html>
<html>
<head>
    <title>{{ page_title }}</title>
</head>
<body>
    <a href="{% url "home" %}">Go Home</a><br />
    <a href="{{ other_link }}">Go somewhere</a><br />
    {{ some_html|safe }}
</body>
</html>
"""
}


class TestStatikViews(unittest.TestCase):

    def configure_env(self, base_path='/'):
        env = Environment(
                loader=DictLoader(TEST_TEMPLATES),
                extensions=['statik.jinja2ext.StatikUrlExtension']
        )
        env.filters['date'] = filter_datetime
        env.statik_base_url = base_path
        return env

    def test_simple_view_processing(self):
        env = self.configure_env()
        view = StatikView(
                from_string=TEST_SIMPLE_VIEW,
                name='home',
                models={},
                template_env=env,
        )
        env.statik_views = {'home': view}
        processed = view.process(None)
        # we should have produced a single index.html page
        self.assertIn('index.html', processed)

        # parse the XML for this page
        parsed = ET.fromstring(processed['index.html'])
        self.assertEqual('html', parsed.findall('.')[0].tag)
        # test static variable substitution
        self.assertEqual('Test page title', parsed.findall('./head/title')[0].text.strip())
        # test URL tag
        self.assertEqual('/', parsed.findall('./body/a')[0].attrib['href'])
        # test other variable substitution
        self.assertEqual('http://somewhere.com', parsed.findall('./body/a')[1].attrib['href'])
        self.assertEqual('Hello!', parsed.findall('./body/p/b')[0].text.strip())

    def test_non_standard_base_path(self):
        env = self.configure_env(base_path='/some/base/path/')
        view = StatikView(
                from_string=TEST_SIMPLE_VIEW,
                name='home',
                models={},
                template_env=env,
        )
        env.statik_views = {'home': view}
        processed = view.process(None)
        # we should have produced a single index.html page
        self.assertIn('index.html', processed)

        # parse the XML for this page
        parsed = ET.fromstring(processed['index.html'])
        self.assertEqual('html', parsed.findall('.')[0].tag)
        # test URL tag
        self.assertEqual('/some/base/path/', parsed.findall('./body/a')[0].attrib['href'])


if __name__ == "__main__":
    unittest.main()
