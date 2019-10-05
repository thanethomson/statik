# -*- coding: utf-8 -*-

import os.path
import xml.etree.ElementTree as ET
import unittest

from statik.generator import generate


class TestMarkdownPermalinksExtension(unittest.TestCase):

    def test_in_memory(self):
        test_path = os.path.dirname(os.path.realpath(__file__))
        output_data = generate(
            os.path.join(test_path, 'data-themed', 'config-permalinks.yml'),
            os.path.join(test_path, 'data-themed'),
            in_memory=True
        )

        self.assertIn('index.html', output_data)
        self.assertIn('test', output_data)
        self.assertIn('index.html', output_data['test'])

        tree = ET.fromstring(output_data['test']['index.html'])
        heading2 = tree.findall('./body/h2')[0]
        self.assertEqual('heres-a-heading', heading2.get('id'))
        permalink2 = tree.findall('./body/h2/a')[0]
        self.assertEqual('#heres-a-heading', permalink2.get('href'))
        self.assertEqual('permalink', permalink2.get('class'))
        self.assertEqual('Permalink to this heading', permalink2.get('title'))

        heading3 = tree.findall('./body/h3')[0]
        self.assertEqual('heres-another-sub-heading', heading3.get('id'))
        permalink3 = tree.findall('./body/h3/a')[0]
        self.assertEqual('#heres-another-sub-heading', permalink3.get('href'))
        self.assertEqual('permalink', permalink3.get('class'))
        self.assertEqual('Permalink to this heading', permalink3.get('title'))


if __name__ == "__main__":
    unittest.main()
