# -*- coding:utf-8 -*-

import unittest

from statik.models import StatikModel
from statik.fields import *
from statik.errors import *


TEST_MODEL_VALID = """string-field: String
datetime-field: DateTime
int-field: Integer
bool-field: Boolean
content-field: Content
text-field: Text
"""

TEST_MODEL_INVALID_FK = """string-field: String
other-field: MissingModelName
"""

TEST_MODEL_VALID_FK = """string-field: String
other-field: OtherModel
"""


class TestStatikModels(unittest.TestCase):

    def test_invalid_model(self):
        with self.assertRaises(ValueError):
            StatikModel()

    def test_model_from_string(self):
        model = StatikModel(
            name='TestModel',
            from_string=TEST_MODEL_VALID,
            model_names=['TestModel']
        )
        self.assertEqual('TestModel', model.name)
        self.assertIsInstance(getattr(model, 'string_field'), StatikStringField)
        self.assertIsInstance(getattr(model, 'datetime_field'), StatikDateTimeField)
        self.assertIsInstance(getattr(model, 'int_field'), StatikIntegerField)
        self.assertIsInstance(getattr(model, 'bool_field'), StatikBooleanField)
        self.assertIsInstance(getattr(model, 'content_field'), StatikContentField)
        self.assertIsInstance(getattr(model, 'text_field'), StatikTextField)

    def test_model_invalid_fk(self):
        with self.assertRaises(InvalidFieldTypeError):
            StatikModel(
                name='TestModel',
                from_string=TEST_MODEL_INVALID_FK,
                model_names=['TestModel']
            )

    def test_model_valid_fk(self):
        model = StatikModel(
            name='TestModel',
            from_string=TEST_MODEL_VALID_FK,
            model_names=['TestModel', 'OtherModel']
        )
        self.assertEqual('TestModel', model.name)
        self.assertIsInstance(getattr(model, 'string_field'), StatikStringField)
        self.assertIsInstance(getattr(model, 'other_field'), StatikForeignKeyField)
        self.assertEqual('OtherModel', model.other_field.field_type)


if __name__ == "__main__":
    unittest.main()
