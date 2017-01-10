# -*- coding: utf-8 -*-

from __future__ import unicode_literals

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

        # parse the home page
        homepage = ET.fromstring(output_data['index.html'])
        self.assertEqual('Home - Theme 1', homepage.findall('./head/title')[0].text.strip())
        self.assertEqual('/assets/theme1.css', homepage.findall('./head/link')[0].attrib['href'])

    def test_theme2(self):
        test_path = os.path.dirname(os.path.realpath(__file__))
        output_data = generate(
            os.path.join(test_path, 'data-themed', 'config-theme2.yml'),
            os.path.join(test_path, 'data-themed'),
            in_memory=True,
        )

        self.assertIn('index.html', output_data)

        # parse the home page
        homepage = ET.fromstring(output_data['index.html'])
        self.assertEqual('Home - Theme 2', homepage.findall('./head/title')[0].text.strip())
        self.assertEqual('/assets/theme2.css', homepage.findall('./head/link')[0].attrib['href'])


if __name__ == "__main__":
    unittest.main()
