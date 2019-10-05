# -*- coding:utf-8 -*-

import unittest
try:
    import unittest.mock as mock
except ImportError:
    import mock

import psycopg2

from statik.external_database import *
from statik.errors import *


class TestExternalDatabase(unittest.TestCase):

    def test_params(self):
        with self.assertRaises(ProjectConfigurationError):
            ExternalDatabase()

        with self.assertRaises(ProjectConfigurationError):
            ExternalDatabase({})

        ExternalDatabase({
            'type': 'fantastic_database',
            'override': True,
        })

    def test_invalid_factory(self):
        external_database = ExternalDatabase({
            'type': 'fantastic_database',
        })

        with self.assertRaises(ProjectConfigurationError):
            external_database.factory()

    def test_valid_factory(self):
        external_database = ExternalDatabase({
            'type': 'fantastic_database',
            'override': False,
        })

        with mock.patch.dict(
            'statik.external_database.ExternalDatabase._external_databases',
            {'fantastic_database': lambda x, y: (x, y)},
        ):
            external_database.factory()


class TestPostgreSQL(unittest.TestCase):

    def setUp(self):
        self.model = mock.Mock()
        self.model.field_names = ['first_name', 'last_name', 'favorite']
        self.model.name = 'person'

    @mock.patch('psycopg2.connect')
    def test_valid_to_dict(self, c):
        mock_psycopg2(connect=c, fetch_list=[('foo', 'bar', 'egg')])

        self.assertEqual(
            PostgreSQL({
                'type': 'fantastic_database'
            }).to_dict(self.model, None),
            {
                'first-name': 'foo',
                'last-name': 'bar',
                'favorite': 'egg',
            },
        )

    @mock.patch('psycopg2.connect')
    def test_invalid_to_dict(self, c):
        mock_psycopg2(connect=c, invalid=True, fetch_list=[])

        with self.assertRaises(ExternalDatabaseError):
            PostgreSQL({
                'type': 'fantastic_database'
            }).to_dict(self.model, None)

    @mock.patch('builtins.open', new_callable=mock.mock_open)
    @mock.patch('yaml.dump')
    @mock.patch('psycopg2.connect')
    def test_valid_write_files(self, c, mock_dump, mock_open):
        mock_psycopg2(
            connect=c,
            fetch_list=[
                ('primary key',),
                None,
                ('foo', 'bar', 'egg'),
            ],
        )
        c.return_value.cursor.return_value.fetchone.return_value = [
            ('primary key',),
            None,
            ('foo', 'bar', 'egg'),
        ]

        PostgreSQL({
            'type': 'fantastic_database'
        }).write_files('path/to/something', [self.model])

        mock_dump.assert_called_once_with(
            {
                'first-name': 'foo',
                'last-name': 'bar',
                'favorite': 'egg',
            },
            mock_open(),
            default_flow_style=False,
        )

    @mock.patch('psycopg2.connect')
    def test_invalid_write_files(self, c):
        mock_psycopg2(connect=c, invalid=True, fetch_list=[])

        with self.assertRaises(ExternalDatabaseError):
            PostgreSQL({
                'type': 'fantastic_database'
            }).write_files('path/to/something', [self.model])


def mock_psycopg2(**kwargs):
    cursor = kwargs.pop('connect').return_value.cursor.return_value

    if kwargs.pop('invalid', False):
        cursor.execute.side_effect = psycopg2.ProgrammingError

    cursor.query.return_value = kwargs.pop('query', 'A query')

    cursor.fetchone.side_effect = kwargs.pop('fetch_list')
