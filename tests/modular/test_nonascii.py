# -*- coding:utf-8 -*-

import unittest

from statik.common import ContentLoadable
from statik.markdown_config import MarkdownConfig


TEST_MARKDOWN_CONTENT = """---
title: This is a “title” with some non-standard characters

unicode:
    - "\u2ffa"
    - "\u2ffb"
---
This is the “Markdown” body with some other non-standard characters.
"""


class TestNonAsciiChars(unittest.TestCase):

    def test_parsing(self):
        parsed = ContentLoadable(
            from_string=TEST_MARKDOWN_CONTENT,
            file_type="markdown",
            name="test",
            markdown_config=MarkdownConfig()
        )
        self.assertEqual(
            "This is a “title” with some non-standard characters",
            parsed.vars['title'],
        )
        self.assertEqual(
            ['⿺', '⿻'],
            parsed.vars['unicode']
        )
        self.assertEqual(
            "<p>This is the “Markdown” body with some other non-standard characters.</p>",
            parsed.content
        )


if __name__ == "__main__":
    unittest.main()
