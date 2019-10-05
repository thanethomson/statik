# -*- coding:utf-8 -*-

import os.path
import unittest
import xml.etree.ElementTree as ET

from statik.views import *
from statik.utils import add_url_path_component
from statik.filters import filter_datetime
from statik.templating import *

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
    <img src="{% asset "sitelogo.png" %}" />
</body>
</html>
""",
    'rss.xml': """<?xml version="1.0" encoding="utf-8" standalone="yes" ?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{{ feed_title }}</title>
    <link>http://somewhere.com/</link>

    <item>
      <title>Sample post</title>
      <link>http://somewhere.com/2016/02/24/some-post/</link>
      <pubDate>Wed, 24 Feb 2016 11:12:41 +0200</pubDate>
      <guid>http://somewhere.com/2016/02/24/some-post/</guid>
    </item>
  </channel>
</rss>
"""
}

TEST_XML_VIEW = """path: /index.xml
template: rss.xml
context:
  static:
    feed-title: My RSS Feed
"""


class MockStatikJinjaTemplateProvider(StatikTemplateProvider):

    def __init__(self, templates_dict=TEST_TEMPLATES, base_path="/"):
        self.env = Environment(
            loader=DictLoader(templates_dict),
            extensions=[
                'statik.jinja2ext.StatikUrlExtension',
                'statik.jinja2ext.StatikAssetExtension'
            ]
        )
        self.env.filters['date'] = filter_datetime
        self.env.statik_base_url = base_path
        self.env.statik_base_asset_url = add_url_path_component(
            base_path,
            'assets',
        )

    def reattach_project_views(self):
        pass

    def load_template(self, name, full_path=None):
        return StatikJinjaTemplate(self, self.env.get_template(name))

    def create_template(self, s):
        return StatikJinjaTemplate(self, self.env.from_string(s))


class MockStatikTemplateEngine(StatikTemplateEngine):

    def __init__(self, templates_dict=TEST_TEMPLATES, base_path="/"):
        self.provider = MockStatikJinjaTemplateProvider(templates_dict=templates_dict, base_path=base_path)

    def load_template(self, name):
        # append the default file extension
        _, ext = os.path.splitext(name)
        if ext is None or len(ext) == 0:
            name += ".html"
        return self.provider.load_template(name)

    def create_template(self, s, provider_name=None):
        return self.provider.create_template(s)


class TestStatikJinja2Views(unittest.TestCase):

    def test_simple_view_processing(self):
        engine = MockStatikTemplateEngine()
        view = StatikView(
                from_string=TEST_SIMPLE_VIEW,
                name='home',
                models={},
                template_engine=engine
        )
        engine.provider.env.statik_views = {'home': view}
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
        # Test the new {% asset %} tag
        self.assertEqual("/assets/sitelogo.png", parsed.findall("./body/img")[0].attrib['src'])

    def test_non_standard_base_path(self):
        engine = MockStatikTemplateEngine(base_path='/some/base/path/')
        view = StatikView(
                from_string=TEST_SIMPLE_VIEW,
                name='home',
                models={},
                template_engine=engine
        )
        engine.provider.env.statik_views = {'home': view}
        processed = view.process(None)
        # we should have produced a single index.html page
        self.assertIn('index.html', processed)

        # parse the XML for this page
        parsed = ET.fromstring(processed['index.html'])
        self.assertEqual('html', parsed.findall('.')[0].tag)
        # test URL tag
        self.assertEqual('/some/base/path/', parsed.findall('./body/a')[0].attrib['href'])
        # Test the new {% asset %} tag
        self.assertEqual("/some/base/path/assets/sitelogo.png", parsed.findall("./body/img")[0].attrib['src'])

    def test_xml_generation(self):
        engine = MockStatikTemplateEngine()
        view = StatikView(
                from_string=TEST_XML_VIEW,
                name='rssfeed',
                models={},
                template_engine=engine
        )
        processed = view.process(None)
        self.assertIn('index.xml', processed)
        self.assertEqual(1, len(processed))

        # parse the generated XML
        parsed = ET.fromstring(processed['index.xml'])
        self.assertEqual('rss', parsed.findall('.')[0].tag)
        self.assertEqual('My RSS Feed', parsed.findall('./channel/title')[0].text.strip())


if __name__ == "__main__":
    unittest.main()
