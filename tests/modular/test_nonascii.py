# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import unittest

from statik.common import ContentLoadable
from statik.markdown_config import MarkdownConfig


TEST_MARKDOWN_CONTENT = """---
title: This is a “title” with some non-standard characters
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
            "<p>This is the “Markdown” body with some other non-standard characters.</p>",
            parsed.content
        )


if __name__ == "__main__":
    unittest.main()
