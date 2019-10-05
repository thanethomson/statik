# -*- coding: utf-8 -*-
"""Regression test for issue #49."""

import unittest
import os.path
from xml.etree import ElementTree as ET

from statik.generator import generate


class TestForAdditionalPathSegmentInjection(unittest.TestCase):

    def test_issue(self):
        test_path = os.path.dirname(os.path.realpath(__file__))
        output_data = generate(
            os.path.join(test_path, 'data-non-root-base'),
            in_memory=True
        )
        self.assertIn('albums', output_data)
        self.assertIn('browse', output_data['albums'])
        self.assertIn('index.html', output_data['albums']['browse'])
        self.assertIn('test-album1', output_data['albums'])
        self.assertIn('index.html', output_data['albums']['test-album1'])
        self.assertIn('test-album2', output_data['albums'])
        self.assertIn('index.html', output_data['albums']['test-album2'])

        html = ET.fromstring(output_data['albums']['browse']['index.html'])
        self.assertEqual('Browse Albums', html.find('head/title').text.strip())
        album_els = [el for el in html.findall('body/ul/li/a')]
        self.assertEqual(2, len(album_els))
        self.assertEqual('Test Album 2', album_els[0].text.strip())
        self.assertEqual(
            '/non/standard/albums/test-album2/',
            album_els[0].attrib['href']
        )
        self.assertEqual('Test Album 1', album_els[1].text.strip())
        self.assertEqual(
            '/non/standard/albums/test-album1/',
            album_els[1].attrib['href']
        )
