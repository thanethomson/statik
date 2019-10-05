# -*- coding:utf-8 -*-

import os
import os.path
import xml.etree.ElementTree as ET
import unittest
import json
import re

import lipsum
import logging

from statik.project import StatikProject
from statik.generator import generate
from statik.utils import strip_el_text
from statik.errors import MissingTemplateError, SafetyViolationError


logger = logging.getLogger(__name__)
DEBUG = (os.environ.get('DEBUG', "false") in ["true", "1"])
LOGGERS = os.environ.get('LOGGERS', "statik").split(",")

EXPECTED_HTACCESS_CONTENT = """AuthUserFile /usr/local/username/safedirectory/.htpasswd
AuthGroupFile /dev/null
AuthName "Please Enter Password"
AuthType Basic
Require valid-user""".strip()


class TestSimpleStatikIntegration(unittest.TestCase):

    def setUp(self):
        if DEBUG:
            logging.basicConfig(
                level=logging.WARNING,
                format='%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s',
            )
            for logger_name in LOGGERS:
                logger_pkg = logging.getLogger(logger_name)
                logger_pkg.setLevel(logging.DEBUG)

            logger.debug("")
            logger.debug("----------- TEST START -----------")
            logger.debug("")
        else:
            logging.basicConfig(level=logging.CRITICAL)

    def test_safe_mode(self):
        test_path = os.path.dirname(os.path.realpath(__file__))
        project = StatikProject(os.path.join(test_path, 'data-simple'), safe_mode=True)
        caught = False
        try:
            project.generate(
                in_memory=True
            )
        except MissingTemplateError:
            caught = True
        except SafetyViolationError:
            caught = True
        self.assertTrue(caught, "Safe mode generation must raise an appropriate exception when attempting to "
                                "generate content for an unsafe project.")

    def test_in_memory(self):
        test_path = os.path.dirname(os.path.realpath(__file__))

        # Run the Statik generator on our unit test data project, put the
        # result in memory
        output_data = generate(
            os.path.join(test_path, 'data-simple'),
            in_memory=True
        )

        # Check that the home page is there
        self.assertIn('index.html', output_data)

        # Check that the generated .htaccess file is in the root of the output data
        self.assertIn('.htaccess', output_data)
        self.assertEqual(EXPECTED_HTACCESS_CONTENT, output_data['.htaccess'].strip())

        # Check that the generated posts are there
        self.assert_path_exists("2018/02/12/unicode-in-markdown-test/index.html", output_data)
        self.assert_path_exists("2018/01/20/test-datetime-format/index.html", output_data)
        self.assert_path_exists("2016/06/12/andrew-hello-world/index.html", output_data)
        self.assert_path_exists("2016/06/18/second-post/index.html", output_data)
        self.assert_path_exists("2016/06/25/andrew-second-post/index.html", output_data)
        self.assert_path_exists("2016/06/30/tables-test/index.html", output_data)
        self.assert_path_exists("tag-testing/index.html", output_data)
        self.assert_path_exists("overlap/index.html", output_data)
        self.assert_path_exists("overlap/andrew-hello-world/index.html", output_data)
        self.assert_path_exists("overlap/my-first-post/index.html", output_data)
        self.assert_path_exists("overlap/second-post/index.html", output_data)
        self.assert_path_exists("overlap/andrew-second-post/index.html", output_data)

        # Check that the paged posts exist
        self.assert_path_exists("paged-posts/1/index.html", output_data)
        self.assert_path_exists("paged-posts/2/index.html", output_data)
        self.assert_path_exists("paged-posts/3/index.html", output_data)
        self.assert_path_exists("paged-posts/4/index.html", output_data)

        # Check that the Unicode support for Markdown works as intended
        self.assert_unicode_content_compiles(output_data)

        # Check that the homepage compiles properly
        self.assert_homepage_compiles(output_data['index.html'])

        # Check that the post "my-first-post" compiles properly
        self.assert_my_first_post_compiles(self.assert_path_exists("2016/06/15/my-first-post/index.html", output_data))

        # Check that the two bios compiled properly
        self.assert_michael_bio_compiles(self.assert_path_exists("bios/michael/index.html", output_data))
        self.assert_andrew_bio_compiles(self.assert_path_exists("bios/andrew/index.html", output_data))

        # Test the for-each context rendering
        self.assert_by_author_andrew_compiles(self.assert_path_exists("by-author/andrew/index.html", output_data))
        self.assert_by_author_michael_compiles(self.assert_path_exists("by-author/michael/index.html", output_data))

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
        self.assertEqual('Page 1 of 4', pp.findall('./head/title')[0].text.strip())
        self.assertEqual('Page 1 of 4', pp.findall('./body/h1')[0].text.strip())
        pp_els = pp.findall('./body/ul/li/a')
        pp_links = [el.attrib['href'] for el in pp_els]
        pp_link_titles = [el.text.strip() for el in pp_els]
        self.assertEqual(
            [
                '/2018/02/12/unicode-in-markdown-test/',
                '/2018/01/20/test-datetime-format/'
            ],
            pp_links,
        )
        self.assertEqual(
            [
                'Testing Unicode θ in Markdown content (issues #50 and #63)',
                'Testing DateTime format (as per issue #59)'
            ],
            pp_link_titles,
        )

        pp = ET.fromstring(output_data['paged-posts']['2']['index.html'])
        self.assertEqual('html', pp.findall('.')[0].tag)
        self.assertEqual('Page 2 of 4', pp.findall('./head/title')[0].text.strip())
        self.assertEqual('Page 2 of 4', pp.findall('./body/h1')[0].text.strip())
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

        pp = ET.fromstring(output_data['paged-posts']['3']['index.html'])
        self.assertEqual('html', pp.findall('.')[0].tag)
        self.assertEqual('Page 3 of 4', pp.findall('./head/title')[0].text.strip())
        self.assertEqual('Page 3 of 4', pp.findall('./body/h1')[0].text.strip())
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

        pp = ET.fromstring(output_data['paged-posts']['4']['index.html'])
        self.assertEqual('html', pp.findall('.')[0].tag)
        self.assertEqual('Page 4 of 4', pp.findall('./head/title')[0].text.strip())
        self.assertEqual('Page 4 of 4', pp.findall('./body/h1')[0].text.strip())
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

        self.assert_mlalchemy_complex_path_view_compiles(output_data)
        self.assert_homepage_compiles(self.assert_path_exists("mlalchemy/posts/index.html", output_data))
        self.assert_json_data_compiles(output_data)
        self.assert_generated_js_compiles(output_data)

    def assert_homepage_compiles(self, page_content):
        # Parse the home page's XHTML content
        homepage = ET.fromstring(page_content)
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
                '/2018/02/12/unicode-in-markdown-test/',
                '/2018/01/20/test-datetime-format/',
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
                'Testing Unicode θ in Markdown content (issues #50 and #63)',
                'Testing DateTime format (as per issue #59)',
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
        self.assertEqual("John Johnson", homepage.findall("./body/div[@class='all-authors']/ul/li")[1].text.strip())
        self.assertEqual("Michael Anderson", homepage.findall("./body/div[@class='all-authors']/ul/li")[2].text.strip())
        # Test the new {% asset %} tag
        self.assertEqual("/assets/testfile.txt", homepage.findall("./body/div[@class='download']/a")[0].attrib['href'])

        # Test the Lorem Ipsum generators
        self.assertEqual(
            100,
            lipsum.count_words(homepage.findall("./body/div[@class='lorem-ipsum']/p")[0].text.strip())
        )
        self.assertEqual(
            5,
            lipsum.count_sentences(homepage.findall("./body/div[@class='lorem-ipsum']/p")[1].text.strip())
        )
        self.assertTrue(
            lipsum.count_words(homepage.findall("./body/div[@class='lorem-ipsum']/p")[2].text.strip()) > 1
        )

        # check the generated script URL - that it has no trailing slash (issue #48)
        script = homepage.find('body/script')
        self.assertIsNotNone(script)
        self.assertEqual('/scripts/generated.js', script.attrib['src'])

    def assert_my_first_post_compiles(self, content):
        post = ET.fromstring(content)
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

    def assert_michael_bio_compiles(self, content):
        bio = ET.fromstring(content)
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

    def assert_andrew_bio_compiles(self, content):
        bio = ET.fromstring(content)
        self.assertEqual('html', bio.findall('.')[0].tag)
        self.assertEqual('Andrew Michaels', bio.findall('./head/title')[0].text.strip())
        self.assertEqual('mailto:amichaels@somewhere.com', bio.findall(".//div[@class='meta']/a")[0].attrib['href'])
        self.assertEqual('Contact Andrew', bio.findall(".//div[@class='meta']/a")[0].text.strip())
        bio_content = bio.findall(".//div[@class='content']/p")[0]
        bio_content_els = [el for el in bio_content]
        self.assertEqual('em', bio_content_els[0].tag)
        bio_content_text = strip_el_text(bio_content, max_depth=1)
        self.assertEqual("Here's Andrew's bio!", bio_content_text)

    def assert_by_author_andrew_compiles(self, content):
        posts_by_author = ET.fromstring(content)
        self.assertEqual('html', posts_by_author.findall('.')[0].tag)
        self.assertEqual('Posts by Andrew', posts_by_author.findall('./head/title')[0].text.strip())
        self.assertEqual('Posts by Andrew', posts_by_author.findall('./body/h1')[0].text.strip())
        links_by_author_els = posts_by_author.findall('.//li/a')
        links_by_author = [el.attrib['href'] for el in links_by_author_els]
        link_titles_by_author = [el.text.strip() for el in links_by_author_els]
        self.assertEqual(
            [
                '/2018/01/20/test-datetime-format/',
                '/2016/06/30/tables-test/',
                '/2016/06/25/andrew-second-post/',
                '/2016/06/12/andrew-hello-world/'
            ],
            links_by_author
        )
        self.assertEqual(
            [
                'Testing DateTime format (as per issue #59)',
                'Testing Markdown tables',
                'Andrew\'s Second Post',
                'Andrew says Hello World'
            ],
            link_titles_by_author,
        )

    def assert_by_author_michael_compiles(self, content):
        posts_by_author = ET.fromstring(content)
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

    def assert_mlalchemy_complex_path_view_compiles(self, output_data):
        self.assert_path_exists("mlalchemy/andrew-hello-world/index.html", output_data)
        self.assert_path_exists("mlalchemy/my-first-post/index.html", output_data)
        self.assert_path_exists("mlalchemy/second-post/index.html", output_data)
        self.assert_path_exists("mlalchemy/andrew-second-post/index.html", output_data)
        self.assert_path_exists("mlalchemy/tables-test/index.html", output_data)

        self.assertEqual(
            output_data['mlalchemy']['andrew-hello-world']['index.html'],
            output_data['2016']['06']['12']['andrew-hello-world']['index.html']
        )

    def assert_path_exists(self, path, output_data):
        path_parts = path.split("/")
        cur_dict = output_data
        for part in path_parts:
            self.assertIn(part, cur_dict)
            cur_dict = cur_dict[part]
        return cur_dict

    def assert_json_data_compiles(self, output_data):
        self.assertIn('data', output_data)
        self.assertIn('authors', output_data['data'])
        self.assertIn('andrew.json', output_data['data']['authors'])
        self.assertIn('michael.json', output_data['data']['authors'])
        self.check_author_json(
            json.loads(output_data['data']['authors']['andrew.json']),
            'Andrew',
            'Michaels',
            'amichaels@somewhere.com'
        )
        self.check_author_json(
            json.loads(output_data['data']['authors']['michael.json']),
            'Michael',
            'Anderson',
            'manderson@somewhere.com'
        )

    def check_author_json(self, author_json, first_name, last_name, email):
        self.assertIn('firstName', author_json)
        self.assertIn('lastName', author_json)
        self.assertIn('email', author_json)
        self.assertEqual(first_name, author_json['firstName'])
        self.assertEqual(last_name, author_json['lastName'])
        self.assertEqual(email, author_json['email'])

    def assert_generated_js_compiles(self, output_data):
        self.assertIn('scripts', output_data)
        self.assertIn('generated.js', output_data['scripts'])
        lines = output_data['scripts']['generated.js'].split('\n')
        last_line = None
        counter = len(lines) - 1
        self.assertGreater(counter, 3)
        while counter >= 0 and last_line is None:
            if lines[counter] and len(lines[counter]) > 0:
                last_line = lines[counter]
            counter -= 1
        # check that the JavaScript was properly generated
        self.assertEqual("window.alert('Hello world! This is Unit Test Project');", last_line)

    def assert_unicode_content_compiles(self, output_data):
        src = output_data['2018']['02']['12']['unicode-in-markdown-test']['index.html']
        title = re.search(r'<title>(.+)</title>', src).group(1)
        self.assertEqual(
            "Testing Unicode θ in Markdown content (issues #50 and #63)",
            title
        )
        body = re.search(
            r'<div class="content">(.+)<p>(.+)</p>(.+)</div>',
            src.replace('\n', ' ')
        ).group(2)
        self.assertEqual(
            "Here's some Markdown with some θ more special characters, and even some " +
            "emojis 😆. Here we also have a special character in <code>θ</code> code.",
            body
        )


if __name__ == "__main__":
    unittest.main()
