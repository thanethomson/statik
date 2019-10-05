# -*- coding: utf-8 -*-
"""Regression test for issue #51."""

import unittest
import os.path
from xml.etree import ElementTree as ET

from statik.generator import generate


class TestStaticPagesFromProjectDynamicContext(unittest.TestCase):

    def test_issue(self):
        test_path = os.path.dirname(os.path.realpath(__file__))
        output_data = generate(
            os.path.join(test_path, 'data-non-root-base'),
            in_memory=True
        )
        self.assertIn('index.html', output_data)
        self.assertIn('about', output_data)
        self.assertIn('index.html', output_data['about'])
        self.assertIn('contact', output_data)
        self.assertIn('index.html', output_data['contact'])

        html = ET.fromstring(output_data['index.html'])
        static_page_links = html.findall("body/div[@class='menu']/ul/li/a")
        self.assertEqual(2, len(static_page_links))
        self.assertEqual('/non/standard/about/', static_page_links[0].attrib['href'])
        self.assertEqual('/non/standard/contact/', static_page_links[1].attrib['href'])

        self.assert_static_page_compiles(
            output_data['about']['index.html'],
            "About",
            "Here's the About page."
        )
        self.assert_static_page_compiles(
            output_data['contact']['index.html'],
            "Contact",
            "Here's how to contact us."
        )

    def assert_static_page_compiles(self, content, expected_title, expected_body):
        html = ET.fromstring(content)
        title = html.find('head/title')
        self.assertEqual(expected_title, title.text.strip())
        body = html.find('body/p')
        self.assertEqual(expected_body, body.text.strip())
