# -*- codig: utf-8 -*-

import os.path

import psycopg2
import yaml

from statik.errors import *
from statik.utils import camel_to_snake


__all__ = [
    'ExternalDatabase',
    'PostgreSQL',
]


class ExternalDatabase(object):

    _external_databases = {}

    def __init__(self, params=None, error_context=None):
        self.error_context = error_context or StatikErrorContext()

        if not isinstance(params, dict):
            raise ProjectConfigurationError(
                message="External database configuration parameters must be a dictionary.",
                context=self.error_context,
            )
        self.params = params

        try:
            self.type = self.params.pop('type')
        except KeyError:
            raise ProjectConfigurationError(
                message="External database configuration must include type parameter.",
                context=self.error_context,
            )

        self.override = self.params.pop('override', False)


    @classmethod
    def external_database(cls, **kwargs):
        name = kwargs.pop('name', None)

        def decorator(target):
            if not name:
                raise ValueError('name is required to generate external database')
            cls._external_databases[name] = target

            return target

        return decorator


    def factory(self):
        try:
            return ExternalDatabase._external_databases[self.type](self.params, self.error_context)
        except KeyError:
            raise ProjectConfigurationError(
                message="%s is not supported database." % self.type,
                context=self.error_context,
            )


@ExternalDatabase.external_database(name='postgresql')
class PostgreSQL(ExternalDatabase):
    def __init__(self, params=None, error_context=None):
        super(PostgreSQL, self).__init__(params, error_context)

        conn = psycopg2.connect(**self.params)
        self.cur = conn.cursor()

    def write_files(self, base_path, models, **kwargs):
        for model in models:
            try:
                self.cur.execute("SELECT pk FROM %s", camel_to_snake(model.name))
            except psycopg2.ProgrammingError as e:
                self._report_query_error(e)

            pks = []

            row = self.cur.fetchone()
            while row:
                pks.append(row[0])

                row = self.cur.fetchone()

            for pk in pks:
                path = os.path.join(base_path, "%s.yaml" % pk)

                if not self.override and os.path.isfile(path):
                    continue
                with open(path, "w") as f:
                    yaml.dump(self.to_dict(model, pk), f, default_flow_style=False)


    def to_dict(self, model, pk):
        try:
            self.cur.execute(
                "SELECT %s FROM %s WHERE pk = %s",
                (','.join(model.field_names), camel_to_snake(model.name), pk),
            )
        except psycopg2.ProgrammingError as e:
            self._report_query_error(e)

        row = self.cur.fetchone()

        return {name.replace('_', '-'):col for name, col in zip(model.field_names, row)}


    def _report_query_error(self, e):
        raise ExternalDatabaseError(
            message="""Error occured while executing below query:
            %s
            message:
            %s
            """ % (self.cur.query, str(e)),
            context=self.error_context,
        )
