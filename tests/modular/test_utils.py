# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import unittest
import xml.etree.ElementTree as ET

from statik.utils import *

TEST_XML = """
<div class="something">
    Hello world!
    <h1>This is a heading.</h1>
    <a href="#">Now here's a link<span>with some sub-text</span> and a little text left over.</a>
    And some text right at the end.
</div>
"""


class TestStatikUtils(unittest.TestCase):

    def test_strip_el_text(self):
        tree = ET.fromstring(TEST_XML)
        self.assertEqual("Hello world! And some text right at the end.", strip_el_text(tree, max_depth=0))
        self.assertEqual(
            "Hello world! This is a heading. Now here's a link and a little text left over. And some text right at " +
            "the end.",
            strip_el_text(tree, max_depth=1)
        )
        self.assertEqual(
            "Hello world! This is a heading. Now here's a link with some sub-text and a little text left over. "
            "And some text right at the end.",
            strip_el_text(tree, max_depth=2)
        )
        self.assertEqual(
            "Hello world! This is a heading. Now here's a link with some sub-text and a little text left over. "
            "And some text right at the end.",
            strip_el_text(tree, max_depth=3)
        )

    def test_get_url_file_ext(self):
        self.assertEqual(
            get_url_file_ext('index.html'),
            '.html'
        )
        self.assertEqual(
            get_url_file_ext('/'),
            ''
        )
        self.assertEqual(
            get_url_file_ext('/path'),
            ''
        )
        self.assertEqual(
            get_url_file_ext('/longer/path'),
            ''
        )
        self.assertEqual(
            get_url_file_ext('/longer/path/trailing/slash/'),
            ''
        )
        self.assertEqual(
            get_url_file_ext('/path/to/test.html'),
            '.html'
        )
        self.assertEqual(
            get_url_file_ext('.htaccess'),
            '.htaccess'
        )
        self.assertEqual(
            get_url_file_ext('/.dot'),
            '.dot'
        )
        self.assertEqual(
            get_url_file_ext('/directory/with/leading/.dot/'),
            ''
        )
        self.assertEqual(
            get_url_file_ext('/path.htaccess'),
            '.htaccess'
        )
        self.assertEqual(
            get_url_file_ext('/multiple//slashes///slash'),
            ''
        )

    def test_validate_jinja_template(self):
        from mock import patch, mock_open
        with patch("statik.utils.logger.warning") as mock_logger:
            with patch("statik.utils.open", mock_open(read_data="{{ baz }}")):
                validate_jinja_template('/path/to/somewhere', {'posts': 'foo'})
                mock_logger.assert_called_with("'baz' was used in a template, "
                                               "but it's not available to be used. "
                                               "Template: /path/to/somewhere")


if __name__ == "__main__":
    unittest.main()
