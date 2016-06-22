# -*- coding:utf-8 -*-

import os
import os.path
import unittest

from statik.config import StatikConfig


TEST_CONFIG = """project-name: Test Project
base-path: /blog/
assets:
    source: src_static
    dest: dest_static
context:
    static:
        some-project-var: The global value
    dynamic:
        users: session.query(User).filter(User.active == True).all()
"""


class TestStatikProjectConfig(unittest.TestCase):

    def test_invalid_config(self):
        with self.assertRaises(ValueError):
            StatikConfig()

    def test_empty_config(self):
        config = StatikConfig(from_string="")
        self.assertEqual("Untitled project", config.project_name)
        self.assertEqual("/", config.base_path)
        self.assertEqual("assets", config.assets_src_path)
        self.assertEqual("assets", config.assets_dest_path)

    def test_string_config(self):
        config = StatikConfig(from_string=TEST_CONFIG)
        self.assertEqual("Test Project", config.project_name)
        self.assertEqual("/blog/", config.base_path)
        self.assertEqual("src_static", config.assets_src_path)
        self.assertEqual("dest_static", config.assets_dest_path)
        self.assertEqual('The global value', config.context_static['some_project_var'])
        self.assertEqual('session.query(User).filter(User.active == True).all()', config.context_dynamic['users'])

    def test_file_config(self):
        test_path = os.path.dirname(os.path.realpath(__file__))
        config = StatikConfig(os.path.join(test_path, os.pardir, 'integration', 'data-simple', 'config.yml'))
        self.assertEqual("Unit Test Project", config.project_name)
        self.assertEqual("/", config.base_path)


if __name__ == "__main__":
    unittest.main()
