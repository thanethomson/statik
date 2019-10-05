# -*- coding: utf-8 -*-

import os
import os.path
import unittest
import logging
import xml.etree.ElementTree as ET

from statik.generator import generate
from statik.utils import *


DEBUG = (os.environ.get('DEBUG', False) == "True")


class TestStatikMustacheTemplating(unittest.TestCase):

    def setUp(self):
        if DEBUG:
            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s',
            )

    def test_mustache_templating(self):
        test_path = os.path.dirname(os.path.realpath(__file__))

        # Run the Statik generator on our unit test data project, put the
        # result in memory
        output_data = generate(
            os.path.join(test_path, 'data-mustache'),
            in_memory=True
        )
        self.assert_homepage_compiles(output_data)
        self.assert_posts_compile(output_data)

    def assert_homepage_compiles(self, output_data):
        # Check that the home page is there
        self.assertIn('index.html', output_data)
        # Parse it
        homepage = ET.fromstring(output_data['index.html'])
        self.assertEqual('html', homepage.findall(".")[0].tag)
        self.assertEqual('Welcome to the test blog', homepage.findall('./head/title')[0].text.strip())
        self.assertEqual('Home page', homepage.findall('./body/h1')[0].text.strip())
        self.assertEqual(
            'This is some information about the unit test web site.',
            homepage.findall("./body/div[@class='site-summary']")[0].text.strip(),
        )
        # Test the ordering of links on the homepage
        homepage_link_els = homepage.findall('./body/ul/li/a')
        homepage_links = [el.attrib['href'] for el in homepage_link_els]
        homepage_link_titles = [el.text.strip() for el in homepage_link_els]
        self.assertEqual(
            [
                '/2016/06/30/tables-test/',
                '/2016/06/25/andrew-second-post/',
                '/2016/06/18/second-post/',
                '/2016/06/15/my-first-post/',
                '/2016/06/12/andrew-hello-world/'
            ],
            homepage_links,
        )
        self.assertEqual(
            [
                'Testing Markdown tables',
                'Andrew\'s Second Post',
                'Second post',
                'My first post',
                'Andrew says Hello World'
            ],
            homepage_link_titles,
        )
        self.assertEqual("Andrew Michaels", homepage.findall("./body/div[@class='all-authors']/ul/li")[0].text.strip())
        self.assertEqual("Michael Anderson", homepage.findall("./body/div[@class='all-authors']/ul/li")[1].text.strip())

    def assert_posts_compile(self, output_data):
        post_content = self.assert_path_exists("2016/06/12/andrew-hello-world/index.html", output_data)
        self.assert_andrew_hello_world_compiles(post_content)
        post_content = self.assert_path_exists("2016/06/15/my-first-post/index.html", output_data)
        self.assert_my_first_post_compiles(post_content)
        post_content = self.assert_path_exists("2016/06/18/second-post/index.html", output_data)
        self.assert_second_post_compiles(post_content)
        post_content = self.assert_path_exists("2016/06/25/andrew-second-post/index.html", output_data)
        self.assert_andrew_second_post_compiles(post_content)
        post_content = self.assert_path_exists("2016/06/30/tables-test/index.html", output_data)
        self.assert_tables_test_compiles(post_content)

    def assert_andrew_hello_world_compiles(self, html):
        post = ET.fromstring(html)
        self.assertEqual('html', post.findall(".")[0].tag)
        self.assertEqual('Andrew says Hello World', post.findall('./body/h1')[0].text.strip())
        self.assertEqual(
            "This is Andrew's first post. Hello world!",
            post.findall("./body/div[@class='content']/p")[0].text.strip()
        )

    def assert_my_first_post_compiles(self, html):
        post = ET.fromstring(html)
        self.assertEqual('html', post.findall(".")[0].tag)
        self.assertEqual('My first post', post.findall('./body/h1')[0].text.strip())
        post_content = post.findall(".//div[@class='content']/p")[0]
        post_content_els = [el for el in post_content]
        self.assertEqual('strong', post_content_els[0].tag)
        self.assertEqual('Markdown', post_content_els[0].text.strip())
        self.assertEqual('code', post_content_els[1].tag)
        self.assertEqual('HTML', post_content_els[1].text.strip())
        post_content_text = strip_el_text(post_content, max_depth=1)
        self.assertEqual(
            "This is the Markdown content of the first post, which should appropriately be translated into the " +
            "relevant HTML code.",
            post_content_text
        )

    def assert_second_post_compiles(self, html):
        post = ET.fromstring(html)
        self.assertEqual('html', post.findall(".")[0].tag)
        self.assertEqual('Second post', post.findall('./body/h1')[0].text.strip())

    def assert_andrew_second_post_compiles(self, html):
        post = ET.fromstring(html)
        self.assertEqual('html', post.findall(".")[0].tag)
        self.assertEqual("Andrew's Second Post", post.findall('./body/h1')[0].text.strip())

    def assert_tables_test_compiles(self, html):
        post = ET.fromstring(html)
        self.assertEqual('html', post.findall(".")[0].tag)
        self.assertEqual("Testing Markdown tables", post.findall('./body/h1')[0].text.strip())
        headings = post.findall("./body/div[@class='content']/table/thead/tr/th")
        self.assertEqual(3, len(headings))
        self.assertEqual(['Heading 1', 'Heading 2', 'Heading 3'], [el.text.strip() for el in headings])

        cells = post.findall("./body/div[@class='content']/table/tbody/tr/td")
        self.assertEqual(6, len(cells))
        self.assertEqual(
            ['One', 'Two', 'Three', 'Four', 'Five', 'Six'],
            [el.text.strip() for el in cells]
        )

    def assert_path_exists(self, path, output_data):
        path_parts = path.split("/")
        cur_dict = output_data
        for part in path_parts:
            self.assertIn(part, cur_dict)
            cur_dict = cur_dict[part]
        return cur_dict


if __name__ == "__main__":
    unittest.main()
