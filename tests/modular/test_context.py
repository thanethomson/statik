# -*- coding:utf-8 -*-
import unittest

from statik.context import StatikContext
from statik.database import StatikDatabase


class TestStatikContext(unittest.TestCase):
    def test_build_context(self):
        context = StatikContext(dynamic={'render_elm': 'True if my_var > 10 else False'})

        result = context.build(db=StatikDatabase(models={}, data_path=''), extra={'my_var': 30})
        assert result.get('render_elm') is True

        result = context.build(db=StatikDatabase(models={}, data_path=''), extra={'my_var': 5})
        assert result.get('render_elm') is False
