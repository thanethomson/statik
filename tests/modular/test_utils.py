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


if __name__ == "__main__":
    unittest.main()
