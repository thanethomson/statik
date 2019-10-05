# -*- coding: utf-8 -*-

import os.path
import xml.etree.ElementTree as ET
import unittest

from statik.generator import generate


class TestThemedStatikProject(unittest.TestCase):

    def test_theme1(self):
        test_path = os.path.dirname(os.path.realpath(__file__))
        output_data = generate(
            os.path.join(test_path, 'data-themed', 'config-theme1.yml'),
            os.path.join(test_path, 'data-themed'),
            in_memory=True,
        )

        self.assertIn('index.html', output_data)
        self.assertIn('override-me', output_data)
        self.assertIn('index.html', output_data['override-me'])

        # parse the home page
        homepage = ET.fromstring(output_data['index.html'])
        self.assertEqual('Home - Theme 1', homepage.findall('./head/title')[0].text.strip())
        self.assertEqual('/assets/theme1.css', homepage.findall('./head/link')[0].attrib['href'])

        self.check_override_page(output_data['override-me']['index.html'])

    def test_theme2(self):
        test_path = os.path.dirname(os.path.realpath(__file__))
        output_data = generate(
            os.path.join(test_path, 'data-themed', 'config-theme2.yml'),
            os.path.join(test_path, 'data-themed'),
            in_memory=True,
        )

        self.assertIn('index.html', output_data)
        self.assertIn('override-me', output_data)
        self.assertIn('index.html', output_data['override-me'])

        # parse the home page
        homepage = ET.fromstring(output_data['index.html'])
        self.assertEqual('Home - Theme 2', homepage.findall('./head/title')[0].text.strip())
        self.assertEqual('/assets/theme2.css', homepage.findall('./head/link')[0].attrib['href'])

        self.check_override_page(output_data['override-me']['index.html'])

    def check_override_page(self, html):
        page = ET.fromstring(html)
        self.assertEqual('I win all the things!', page.findall('./body')[0].text.strip())


if __name__ == "__main__":
    unittest.main()
