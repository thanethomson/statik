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

        # Check that the generated posts are there
        self.assertIn('2016', output_data)
        self.assertIn('06', output_data['2016'])
        self.assertIn('12', output_data['2016']['06'])
        self.assertIn('15', output_data['2016']['06'])
        self.assertIn('18', output_data['2016']['06'])
        self.assertIn('25', output_data['2016']['06'])
        self.assertIn('andrew-hello-world', output_data['2016']['06']['12'])
        self.assertIn('my-first-post', output_data['2016']['06']['15'])
        self.assertIn('second-post', output_data['2016']['06']['18'])
        self.assertIn('andrew-second-post', output_data['2016']['06']['25'])
        self.assertIn('index.html', output_data['2016']['06']['12']['andrew-hello-world'])
        self.assertIn('index.html', output_data['2016']['06']['15']['my-first-post'])
        self.assertIn('index.html', output_data['2016']['06']['18']['second-post'])
        self.assertIn('index.html', output_data['2016']['06']['25']['andrew-second-post'])

        # Check that the generated author bio is there
        self.assertIn('bios', output_data)
        self.assertIn('michael', output_data['bios'])
        self.assertIn('index.html', output_data['bios']['michael'])

        # Check that the generated posts-by-author pages are there
        self.assertIn('by-author', output_data)
        self.assertIn('andrew', output_data['by-author'])
        self.assertIn('michael', output_data['by-author'])
        self.assertIn('index.html', output_data['by-author']['andrew'])
        self.assertIn('index.html', output_data['by-author']['michael'])

        # Parse the home page's XHTML content
        homepage = ET.fromstring(output_data['index.html'])
        self.assertEqual('html', homepage.findall('.')[0].tag)
        self.assertEqual('Welcome to the test blog', homepage.findall('./head/title')[0].text.strip())
        self.assertEqual('Home page', homepage.findall('./body/h1')[0].text.strip())
        # Test the project-wide static context variables
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
                '/2016/06/25/andrew-second-post/',
                '/2016/06/18/second-post/',
                '/2016/06/15/my-first-post/',
                '/2016/06/12/andrew-hello-world/',
            ],
            homepage_links,
        )
        self.assertEqual(
            [
                'Andrew\'s Second Post',
                'Second post',
                'My first post',
                'Andrew says Hello World',
            ],
            homepage_link_titles,
        )

        # Test the project-wide dynamic context variables
        self.assertEqual("Andrew Michaels", homepage.findall("./body/div[@class='all-authors']/ul/li")[0].text.strip())
        self.assertEqual("Michael Anderson", homepage.findall("./body/div[@class='all-authors']/ul/li")[1].text.strip())
        # Test the new {% asset %} tag
        self.assertEqual("/assets/testfile.txt", homepage.findall("./body/div[@class='download']/a")[0].attrib['href'])

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
        self.assertEqual(
                "This is the Markdown content of the first post, which should appropriately be translated into the " +
                "relevant HTML code.",
                post_content_text
        )

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

        bio = ET.fromstring(output_data['bios']['andrew']['index.html'])
        self.assertEqual('html', bio.findall('.')[0].tag)
        self.assertEqual('Andrew Michaels', bio.findall('./head/title')[0].text.strip())
        self.assertEqual('mailto:amichaels@somewhere.com', bio.findall(".//div[@class='meta']/a")[0].attrib['href'])
        self.assertEqual('Contact Andrew', bio.findall(".//div[@class='meta']/a")[0].text.strip())
        bio_content = bio.findall(".//div[@class='content']/p")[0]
        bio_content_els = [el for el in bio_content]
        self.assertEqual('em', bio_content_els[0].tag)
        bio_content_text = get_plain_text_in_el(bio_content)
        self.assertEqual("Here's Andrew's bio!", bio_content_text)

        # Test the for-each context rendering
        posts_by_author = ET.fromstring(output_data['by-author']['andrew']['index.html'])
        self.assertEqual('html', posts_by_author.findall('.')[0].tag)
        self.assertEqual('Posts by Andrew', posts_by_author.findall('./head/title')[0].text.strip())
        self.assertEqual('Posts by Andrew', posts_by_author.findall('./body/h1')[0].text.strip())
        links_by_author_els = posts_by_author.findall('.//li/a')
        links_by_author = [el.attrib['href'] for el in links_by_author_els]
        link_titles_by_author = [el.text.strip() for el in links_by_author_els]
        self.assertEqual(
            [
                '/2016/06/25/andrew-second-post/',
                '/2016/06/12/andrew-hello-world/',
            ],
            links_by_author
        )
        self.assertEqual(
            [
                'Andrew\'s Second Post',
                'Andrew says Hello World',
            ],
            link_titles_by_author,
        )

        posts_by_author = ET.fromstring(output_data['by-author']['michael']['index.html'])
        self.assertEqual('html', posts_by_author.findall('.')[0].tag)
        self.assertEqual('Posts by Michael', posts_by_author.findall('./head/title')[0].text.strip())
        self.assertEqual('Posts by Michael', posts_by_author.findall('./body/h1')[0].text.strip())
        links_by_author_els = posts_by_author.findall('.//li/a')
        links_by_author = [el.attrib['href'] for el in links_by_author_els]
        link_titles_by_author = [el.text.strip() for el in links_by_author_els]
        self.assertEqual(
                [
                    '/2016/06/18/second-post/',
                    '/2016/06/15/my-first-post/',
                ],
                links_by_author
        )
        self.assertEqual(
                [
                    'Second post',
                    'My first post',
                ],
                link_titles_by_author,
        )


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
