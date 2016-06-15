# -*- coding:utf-8 -*-

import os.path
import xml.etree.ElementTree as ET
import unittest

import statik


class TestSimpleStatikIntegration(unittest.TestCase):

    def test_in_memory(self):
        test_path = os.path.realpath(__file__)

        # Run the Statik generator on our unit test data project, put the
        # result in memory
        output_data = statik.generate(
            os.path.join(test_path, 'data-simple'),
            in_memory=True,
        )

        # Check that the home page is there
        self.assertIn('index.html', output_data)

        # Check that the generated post is there
        self.assertIn('2016', output_data)
        self.assertIn('06', output_data['2016'])
        self.assertIn('15', output_data['2016']['06'])
        self.assertIn('my-first-post', output_data['2016']['06']['15'])
        self.assertIn('index.html', output_data['2016']['06']['15']['my-first-post'])

        # Check that the generated author bio is there
        self.assertIn('bios', output_data)
        self.assertIn('michael', output_data['bios'])
        self.assertIn('index.html', output_data['bios']['michael']['index.html'])

        # Parse the home page's XHTML content
        homepage = ET.fromstring(output_data['index.html'])
        self.assertEqual('html', homepage.findall('.').tag)
        self.assertEqual('Welcome to the test blog', homepage.findall('./html/head/title').text.strip())
        self.assertEqual('Home page', homepage.findall('./html/body/h1').text.strip())
        self.assertEqual('/2016/06/15/my-first-post/', homepage.findall('./html/body/ul/li/a').attrib['href'])
        self.assertEqual('My first post', homepage.findall('./html/body/ul/li/a').text.strip())

        # TODO: Parse the post page's XHTML content
        # TODO: Parse the bio page's XHTML content


if __name__ == "__main__":
    unittest.main()
