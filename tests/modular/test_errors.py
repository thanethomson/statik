# -*- coding: utf-8 -*-

import unittest
from statik.errors import StatikErrorContext


class TestStatikErrorHandling(unittest.TestCase):

    def test_empty_error_context(self):
        context = StatikErrorContext()
        self.assertIsNone(context.render())

    def test_error_context_with_filename_only(self):
        context = StatikErrorContext(filename="somefilename.yml")
        self.assertEqual("in file \"somefilename.yml\"", context.render())

    def test_complete_error_context(self):
        context = StatikErrorContext(filename="somefilename.yml", line_no=12)
        self.assertEqual("in file \"somefilename.yml\", line 12", context.render())
