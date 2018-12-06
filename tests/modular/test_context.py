# -*- coding:utf-8 -*-
import unittest

import mock

from statik.context import StatikContext
from statik.database import StatikDatabase


class TestStatikContext(unittest.TestCase):
    def test_build_context(self):
        context = StatikContext(dynamic={'render_elm': 'True if my_var > 10 else False'})

        result = context.build(db=StatikDatabase(models={}, data_path=''), extra={'my_var': 30})
        assert result.get('render_elm') is True

        result = context.build(db=StatikDatabase(models={}, data_path=''), extra={'my_var': 5})
        assert result.get('render_elm') is False

    def test_env_var_in_context(self):
        with mock.patch.dict('statik.context.os.environ',
                             {'HOME': 'HOME!!'}):
            context = StatikContext()

            result = context.build(db=StatikDatabase(models={}, data_path=''))
            self.assertEqual(result.get('HOME'), 'HOME!!')
