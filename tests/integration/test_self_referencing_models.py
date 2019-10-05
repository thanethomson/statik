# -*- coding: utf-8 -*-

import unittest
import os.path
import xml.etree.ElementTree as ET
import logging

from statik.generator import generate

logger = logging.getLogger(__name__)
DEBUG = (os.environ.get('DEBUG', "false") in ["true", "1"])
LOGGERS = os.environ.get('LOGGERS', "statik").split(",")


class TestSelfReferencingModels(unittest.TestCase):

    def setUp(self):
        if DEBUG:
            logging.basicConfig(
                level=logging.WARNING,
                format='%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s',
            )
            for logger_name in LOGGERS:
                logger_pkg = logging.getLogger(logger_name)
                logger_pkg.setLevel(logging.DEBUG)
        else:
            logging.basicConfig(level=logging.CRITICAL)

    def test_self_referencing_models(self):
        test_path = os.path.dirname(os.path.realpath(__file__))
        output_data = generate(
            os.path.join(test_path, "data-self-referencing"),
            in_memory=True
        )

        self.assertIn('index.html', output_data)
        homepage = ET.fromstring(output_data['index.html'])
        parents = homepage.findall('body/ul/li')
        self.assertEqual('Parent 1', parents[0].text.strip())
        children = set([c.text.strip() for c in parents[0].findall('ul/li')])
        self.assertEqual({'Child 1.1', 'Child 1.2'}, children)

        self.assertEqual('Parent 2', parents[1].text.strip())
        children = set([c.text.strip() for c in parents[1].findall('ul/li')])
        self.assertEqual({'Child 2.1', 'Child 2.2'}, children)
