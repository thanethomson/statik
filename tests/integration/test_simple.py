# -*- coding:utf-8 -*-

import os.path
import xml.etree.ElementTree as ET
import unittest

import statik


class TestSimpleStatikIntegration(unittest.TestCase):

    def test_in_memory(self):
        test_path = os.path.dirname(os.path.realpath(__file__))

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
        self.assertIn('index.html', output_data['bios']['michael'])

        # Parse the home page's XHTML content
        homepage = ET.fromstring(output_data['index.html'])
        self.assertEqual('html', homepage.findall('.')[0].tag)
        self.assertEqual('Welcome to the test blog', homepage.findall('./head/title')[0].text.strip())
        self.assertEqual('Home page', homepage.findall('./body/h1')[0].text.strip())
        self.assertEqual('/2016/06/15/my-first-post/', homepage.findall('./body/ul/li/a')[0].attrib['href'])
        self.assertEqual('My first post', homepage.findall('./body/ul/li/a')[0].text.strip())

        post = ET.fromstring(output_data['2016']['06']['15']['my-first-post']['index.html'])
        self.assertEqual('html', post.findall('.')[0].tag)
        self.assertEqual('My first post', post.findall('./head/title')[0].text.strip())
        self.assertEqual('2016-06-15', post.findall(".//div[@class='published']")[0].text.strip())
        self.assertEqual('/bios/michael/', post.findall(".//div[@class='author']/a")[0].attrib['href'])
        self.assertEqual('By Michael', post.findall(".//div[@class='author']/a")[0].text.strip())
        post_content = post.findall(".//div[@class='content']/p")[0]
        post_content_els = [el for el in post_content]
        self.assertEqual('strong', post_content_els[0].tag)
        self.assertEqual('Markdown', post_content_els[0].text.strip())
        self.assertEqual('code', post_content_els[1].tag)
        self.assertEqual('HTML', post_content_els[1].text.strip())
        post_content_text = get_plain_text_in_el(post_content)
        self.assertEqual("This is the Markdown content of the first post, which should appropriately be translated into the relevant HTML code.",
            post_content_text)

        bio = ET.fromstring(output_data['bios']['michael']['index.html'])
        self.assertEqual('html', bio.findall('.')[0].tag)
        self.assertEqual('Michael Anderson', bio.findall('./head/title')[0].text.strip())
        self.assertEqual('mailto:manderson@somewhere.com', bio.findall(".//div[@class='meta']/a")[0].attrib['href'])
        self.assertEqual('Contact Michael', bio.findall(".//div[@class='meta']/a")[0].text.strip())
        bio_content = bio.findall(".//div[@class='content']/p")[0]
        bio_content_els = [el for el in bio_content]
        self.assertEqual('strong', bio_content_els[0].tag)
        self.assertEqual('Markdown', bio_content_els[0].text.strip())
        bio_content_text = get_plain_text_in_el(bio_content)
        self.assertEqual("This is Michael's bio, in Markdown format.", bio_content_text)


def strip_str(s):
    """Strips out newlines and whitespace from the given string."""
    return ' '.join([w.strip() for w in s.strip().split('\n')])

def get_plain_text_in_el(el, root_level=True):
    """Strips out all of the plain text within the given XML element, and
    all of its first-level sub-elements.
    """
    # get the sub-elements within this particular element
    sub_els = [e for e in el]
    el_text = strip_str(el.text)
    # if it's not the root-level element, we also want to append any tail text
    if not root_level:
        el_text = ' '.join([el_text, strip_str(el.tail)]).strip()

    return ' '.join([el_text, ] +
        ([get_plain_text_in_el(e, root_level=False) for e in sub_els] if sub_els else [])
    ).strip()

if __name__ == "__main__":
    unittest.main()
