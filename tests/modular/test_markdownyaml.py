# -*- coding:utf-8 -*-

import unittest
from markdown import Markdown

from statik.markdownyaml import MarkdownYamlMetaExtension


TEST_VALID_CONTENT1 = """---
some-variable: Value
other-variable: Another value
yet-another:
    - this
    - is
    - a
    - list
---
This is where the **Markdown** content will go.
"""

TEST_VALID_CONTENT2 = """
This is just some plain old **Markdown** content, without metadata.
"""


class TestMarkdownYamlExtension(unittest.TestCase):

    def test_extension(self):
        md = Markdown(
            extensions=[MarkdownYamlMetaExtension()]
        )
        html = md.convert(TEST_VALID_CONTENT1)
        self.assertEqual("<p>This is where the <strong>Markdown</strong> content will go.</p>", html.strip())
        expected_meta = {
            'some-variable': 'Value',
            'other-variable': 'Another value',
            'yet-another': ['this', 'is', 'a', 'list']
        }
        self.assertEqual(expected_meta, md.meta)

        html = md.convert(TEST_VALID_CONTENT2)
        self.assertEqual("<p>This is just some plain old <strong>Markdown</strong> content, without metadata.</p>", html.strip())
        # no metadata
        self.assertEqual({}, md.meta)
