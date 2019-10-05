# -*- coding:utf-8 -*-

import unittest
from markdown import Markdown
import xml.etree.ElementTree as ET

from statik.markdown_exts import *

import lipsum


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

TEST_PERMALINK_CONTENT = """
# Heading 1

Some text goes here.

## Heading 2
Some sub-text.

### Heading 3
And even more text.

#### Heading 4
It goes on...

##### Heading 5
... and on...

###### Heading 6
... and on. And finally comes to an end.
"""

TEST_LOREM_IPSUM_CONTENT = """
!(lipsum-words:100)

!(lipsum-sentences:5)

!(lipsum-paragraphs:3)
"""

TEST_LOREM_IPSUM_SINGLE_INSTANCES = """
!(lipsum-word)

!(lipsum-sentence)

!(lipsum-paragraph)
"""


class TestMarkdownYamlExtension(unittest.TestCase):

    def test_yaml_extension(self):
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

    def test_permalink_extension(self):
        md = Markdown(
            extensions=[
                MarkdownPermalinkExtension(
                    permalink_text="¶",
                    permalink_class="permalink",
                    permalink_title="Permalink to this headline"
                )
            ]
        )
        html = "<html><body>"+md.convert(TEST_PERMALINK_CONTENT)+"</body></html>"
        tree = ET.fromstring(html)

        for tag_id in range(1, 7):
            heading = tree.findall('./body/h%d' % tag_id)[0]
            self.assertEqual('heading-%d' % tag_id, heading.get('id'))
            link = tree.findall('./body/h%d/a' % tag_id)[0]
            self.assertEqual('#heading-%d' % tag_id, link.get('href'))
            self.assertEqual('permalink', link.get('class'))
            self.assertEqual('Permalink to this headline', link.get('title'))

    def test_lorem_ipsum_extension(self):
        md = Markdown(
            extensions=[
                MarkdownYamlMetaExtension(),
                MarkdownLoremIpsumExtension()
            ]
        )
        html = "<html>"+md.convert(TEST_LOREM_IPSUM_CONTENT)+"</html>"
        tree = ET.fromstring(html)
        p = tree.findall('./p')[0]
        self.assertEqual(100, lipsum.count_words(p.text))

        p = tree.findall('./p')[1]
        self.assertEqual(5, lipsum.count_sentences(p.text))
        self.assertEqual(3, len(tree.findall('./p')[2:]))

        html = "<html>"+md.convert(TEST_LOREM_IPSUM_SINGLE_INSTANCES)+"</html>"
        tree = ET.fromstring(html)
        p = tree.findall('./p')[0]
        self.assertEqual(1, lipsum.count_words(p.text))

        p = tree.findall('./p')[1]
        self.assertEqual(1, lipsum.count_sentences(p.text))
        self.assertEqual(1, len(tree.findall('./p')[2:]))
