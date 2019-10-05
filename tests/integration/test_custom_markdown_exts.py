# -*- coding: utf-8 -*-

import os.path
import xml.etree.ElementTree as ET
import unittest

from statik.generator import generate


class TestCustomMarkdownExtensions(unittest.TestCase):

    def test_in_memory(self):
        test_path = os.path.dirname(os.path.realpath(__file__))
        output_data = generate(
            os.path.join(test_path, 'data-themed', 'config-custom-md-exts.yml'),
            os.path.join(test_path, 'data-themed'),
            in_memory=True
        )

        self.assertIn('index.html', output_data)
        self.assertIn('test', output_data)
        self.assertIn('test-with-code', output_data)
        self.assertIn('index.html', output_data['test'])
        self.assertIn('index.html', output_data['test-with-code'])

        tree = ET.fromstring(output_data['test-with-code']['index.html'])
        self.assertEqual("Test post with some code", tree.findall('./head/title')[0].text.strip())
        self.assertEqual(
            "This should test the codehilite integration.",
            tree.findall('./body/p')[0].text.strip()
        )
        self.assertEqual(
            "codehilite",
            tree.findall('./body/pre')[0].get('class')
        )
        self.assertEqual(
            "language-python",
            tree.findall('./body/pre/code')[0].get('class')
        )

        self.assertEqual(
            "And now some more code, but in a different language:",
            tree.findall('./body/p')[1].text.strip()
        )
        self.assertEqual(
            "codehilite",
            tree.findall('./body/pre')[1].get('class')
        )
        self.assertEqual(
            "language-c",
            tree.findall('./body/pre/code')[1].get('class')
        )


if __name__ == "__main__":
    unittest.main()

