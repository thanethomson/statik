# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import os.path
import xml.etree.ElementTree as ET
import unittest

from statik.generator import generate
from statik.utils import strip_el_text


class TestSimpleStatikIntegration(unittest.TestCase):

    def test_in_memory(self):
        test_path = os.path.dirname(os.path.realpath(__file__))

        # Run the Statik generator on our unit test data project, put the
        # result in memory
        output_data = generate(
            os.path.join(test_path, 'data-simple'),
            in_memory=True,
        )

        # Check that the home page is there
        self.assertIn('index.html', output_data)

        # Check that the generated posts are there
        self.assertIn('2016', output_data)
        self.assertIn('tag-testing', output_data)
        self.assertIn('06', output_data['2016'])
        self.assertIn('12', output_data['2016']['06'])
        self.assertIn('15', output_data['2016']['06'])
        self.assertIn('18', output_data['2016']['06'])
        self.assertIn('25', output_data['2016']['06'])
        self.assertIn('30', output_data['2016']['06'])
        self.assertIn('andrew-hello-world', output_data['2016']['06']['12'])
        self.assertIn('my-first-post', output_data['2016']['06']['15'])
        self.assertIn('second-post', output_data['2016']['06']['18'])
        self.assertIn('andrew-second-post', output_data['2016']['06']['25'])
        self.assertIn('tables-test', output_data['2016']['06']['30'])
        self.assertIn('index.html', output_data['2016']['06']['12']['andrew-hello-world'])
        self.assertIn('index.html', output_data['2016']['06']['15']['my-first-post'])
        self.assertIn('index.html', output_data['2016']['06']['18']['second-post'])
        self.assertIn('index.html', output_data['2016']['06']['25']['andrew-second-post'])
        self.assertIn('index.html', output_data['2016']['06']['30']['tables-test'])
        self.assertIn('index.html', output_data['tag-testing'])
        self.assertIn('overlap', output_data)
        self.assertIn('index.html', output_data['overlap'])
        self.assertIn('andrew-hello-world', output_data['overlap'])
        self.assertIn('index.html', output_data['overlap']['andrew-hello-world'])
        self.assertIn('my-first-post', output_data['overlap'])
        self.assertIn('index.html', output_data['overlap']['my-first-post'])
        self.assertIn('second-post', output_data['overlap'])
        self.assertIn('index.html', output_data['overlap']['second-post'])
        self.assertIn('andrew-second-post', output_data['overlap'])
        self.assertIn('index.html', output_data['overlap']['andrew-second-post'])
        # test for pagination: we expect 3 pages at 2 items per page
        self.assertIn('paged-posts', output_data)
        self.assertIn('1', output_data['paged-posts'])
        self.assertIn('index.html', output_data['paged-posts']['1'])
        self.assertIn('2', output_data['paged-posts'])
        self.assertIn('index.html', output_data['paged-posts']['2'])
        self.assertIn('3', output_data['paged-posts'])
        self.assertIn('index.html', output_data['paged-posts']['3'])

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
        post_content_text = strip_el_text(post_content, max_depth=1)
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
        bio_content_text = strip_el_text(bio_content, max_depth=1)
        self.assertEqual("This is Michael's bio, in Markdown format.", bio_content_text)

        bio = ET.fromstring(output_data['bios']['andrew']['index.html'])
        self.assertEqual('html', bio.findall('.')[0].tag)
        self.assertEqual('Andrew Michaels', bio.findall('./head/title')[0].text.strip())
        self.assertEqual('mailto:amichaels@somewhere.com', bio.findall(".//div[@class='meta']/a")[0].attrib['href'])
        self.assertEqual('Contact Andrew', bio.findall(".//div[@class='meta']/a")[0].text.strip())
        bio_content = bio.findall(".//div[@class='content']/p")[0]
        bio_content_els = [el for el in bio_content]
        self.assertEqual('em', bio_content_els[0].tag)
        bio_content_text = strip_el_text(bio_content, max_depth=1)
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
                '/2016/06/30/tables-test/',
                '/2016/06/25/andrew-second-post/',
                '/2016/06/12/andrew-hello-world/'
            ],
            links_by_author
        )
        self.assertEqual(
            [
                'Testing Markdown tables',
                'Andrew\'s Second Post',
                'Andrew says Hello World'
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

        # Test the custom template tags/filters functionality
        tt = ET.fromstring(output_data['tag-testing']['index.html'])
        self.assertEqual('html', tt.findall('.')[0].tag)
        para_tags = tt.findall('./body/p')
        self.assertEqual('Hello world!', para_tags[0].text.strip())
        self.assertEqual('an uppercase string', para_tags[1].text.strip())

        # Check the contents of the overlapping simple/complex views
        ov = ET.fromstring(output_data['overlap']['index.html'])
        self.assertEqual('html', ov.findall('.')[0].tag)
        self.assertEqual('Overlap Test', ov.findall('./head/title')[0].text.strip())
        self.assertEqual('Overlap Test', ov.findall('./body/h1')[0].text.strip())

        ov = ET.fromstring(output_data['overlap']['andrew-hello-world']['index.html'])
        self.assertEqual('html', ov.findall('.')[0].tag)
        self.assertEqual('Overlap Test', ov.findall('./head/title')[0].text.strip())
        self.assertEqual('Andrew says Hello World', ov.findall('./body/h1')[0].text.strip())

        ov = ET.fromstring(output_data['overlap']['my-first-post']['index.html'])
        self.assertEqual('html', ov.findall('.')[0].tag)
        self.assertEqual('Overlap Test', ov.findall('./head/title')[0].text.strip())
        self.assertEqual('My first post', ov.findall('./body/h1')[0].text.strip())

        ov = ET.fromstring(output_data['overlap']['second-post']['index.html'])
        self.assertEqual('html', ov.findall('.')[0].tag)
        self.assertEqual('Overlap Test', ov.findall('./head/title')[0].text.strip())
        self.assertEqual('Second post', ov.findall('./body/h1')[0].text.strip())

        ov = ET.fromstring(output_data['overlap']['andrew-second-post']['index.html'])
        self.assertEqual('html', ov.findall('.')[0].tag)
        self.assertEqual('Overlap Test', ov.findall('./head/title')[0].text.strip())
        self.assertEqual("Andrew's Second Post", ov.findall('./body/h1')[0].text.strip())

        # Test the Markdown table generation
        tables = ET.fromstring(output_data['2016']['06']['30']['tables-test']['index.html'])
        self.assertEqual('html', tables.findall('.')[0].tag)
        headings = tables.findall("./body/div[@class='content']/table/thead/tr/th")
        self.assertEqual(3, len(headings))
        self.assertEqual(['Heading 1', 'Heading 2', 'Heading 3'], [el.text.strip() for el in headings])

        cells = tables.findall("./body/div[@class='content']/table/tbody/tr/td")
        self.assertEqual(6, len(cells))
        self.assertEqual(
            ['One', 'Two', 'Three', 'Four', 'Five', 'Six'],
            [el.text.strip() for el in cells]
        )

        # Now test for the pagination
        pp = ET.fromstring(output_data['paged-posts']['1']['index.html'])
        self.assertEqual('html', pp.findall('.')[0].tag)
        self.assertEqual('Page 1 of 3', pp.findall('./head/title')[0].text.strip())
        self.assertEqual('Page 1 of 3', pp.findall('./body/h1')[0].text.strip())
        pp_els = pp.findall('./body/ul/li/a')
        pp_links = [el.attrib['href'] for el in pp_els]
        pp_link_titles = [el.text.strip() for el in pp_els]
        self.assertEqual(
            [
                '/2016/06/30/tables-test/',
                '/2016/06/25/andrew-second-post/'
            ],
            pp_links,
        )
        self.assertEqual(
            [
                'Testing Markdown tables',
                'Andrew\'s Second Post'
            ],
            pp_link_titles,
        )

        pp = ET.fromstring(output_data['paged-posts']['2']['index.html'])
        self.assertEqual('html', pp.findall('.')[0].tag)
        self.assertEqual('Page 2 of 3', pp.findall('./head/title')[0].text.strip())
        self.assertEqual('Page 2 of 3', pp.findall('./body/h1')[0].text.strip())
        pp_els = pp.findall('./body/ul/li/a')
        pp_links = [el.attrib['href'] for el in pp_els]
        pp_link_titles = [el.text.strip() for el in pp_els]
        self.assertEqual(
            [
                '/2016/06/18/second-post/',
                '/2016/06/15/my-first-post/'
            ],
            pp_links,
        )
        self.assertEqual(
            [
                'Second post',
                'My first post'
            ],
            pp_link_titles,
        )

        pp = ET.fromstring(output_data['paged-posts']['3']['index.html'])
        self.assertEqual('html', pp.findall('.')[0].tag)
        self.assertEqual('Page 3 of 3', pp.findall('./head/title')[0].text.strip())
        self.assertEqual('Page 3 of 3', pp.findall('./body/h1')[0].text.strip())
        pp_els = pp.findall('./body/ul/li/a')
        pp_links = [el.attrib['href'] for el in pp_els]
        pp_link_titles = [el.text.strip() for el in pp_els]
        self.assertEqual(
            [
                '/2016/06/12/andrew-hello-world/'
            ],
            pp_links,
        )
        self.assertEqual(
            [
                'Andrew says Hello World'
            ],
            pp_link_titles,
        )


if __name__ == "__main__":
    unittest.main()
