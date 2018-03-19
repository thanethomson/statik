# -*- coding:utf-8 -*-

from __future__ import unicode_literals
from future.utils import iteritems
from past.builtins import basestring
from io import open

import os.path
import yaml

from sqlalchemy import String, Integer, Column, Table, ForeignKey, \
    Boolean, DateTime, Text, create_engine
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base

import mlalchemy

from dateutil.parser import parse as dateutil_parse

from statik.common import ContentLoadable
from statik.fields import *
from statik.errors import *
from statik.utils import *
from statik.config import MarkdownConfig
from statik.pagination import *

# utility imports for SQLAlchemy code execution
from datetime import datetime, date, timedelta, time
from sqlalchemy import func, distinct
import sqlalchemy
import math

import logging
logger = logging.getLogger(__name__)

__all__ = [
    'StatikDatabase',
]

SQLALCHEMY_FIELD_MAPPER = {
    'String': String,
    'DateTime': DateTime,
    'Integer': Integer,
    'Boolean': Boolean,
    'Content': Text,
    'Text': Text
}


def set_global(name, val):
    logger.debug('Setting global: %s = %s' % (name, val))
    globals()[name] = val
    set_global.tracked_globals.add(name)
set_global.tracked_globals = set()


def clear_tracked_globals():
    for name in set_global.tracked_globals:
        logger.debug('Clearing tracked global: %s' % name)
        del globals()[name]
    set_global.tracked_globals = set()


class StatikDatabase(object):

    def __init__(self, data_path, models, encoding=None, markdown_config=None,
            error_context=None):
        """Constructor.

        Args:
            data_path: The full path to where the database files can be found.
            models: Loaded model/field data.
            encoding: The encoding to load files as ('utf-8', etc). If 'None', will
                      default to the system-preferred default encoding.
            error_context: An optional StatikErrorContext instance for keeping track of
                the files to which any exceptions are relevant.
        """
        self.encoding = encoding
        self.tables = dict()
        self.data_path = data_path
        self.models = models
        self.markdown_config = markdown_config
        self.error_context = error_context or StatikErrorContext()
        self.engine = create_engine('sqlite:///:memory:')
        self.Base = declarative_base()
        self.session = sessionmaker(bind=self.engine)()
        set_global('session', self.session)
        self.find_backrefs()
        self.create_db(models)

    def find_backrefs(self):
        for model_name, model in iteritems(self.models):
            logger.debug('Attempting to find backrefs for model: %s', model_name)
            try:
                model.find_additional_rels(self.models)
            except Exception as exc:
                raise ModelError(
                    model_name,
                    message="failed to accurately determine model cross-referencing.",
                    orig_exc=exc,
                    context=self.error_context
                )

    def create_db(self, models):
        """Creates the in-memory SQLite database from the model
        configuration."""
        # first create the table definitions
        self.tables = dict(
            [
                (model_name, self.create_model_table(model))
                for model_name, model in iteritems(models)
            ]
        )
        # now create the tables in memory
        logger.debug("Creating %d database table(s)...", len(self.tables))
        try:
            self.Base.metadata.create_all(self.engine)
        except Exception as exc:
            raise StatikError(
                message="Failed to create in-memory data model.",
                orig_exc=exc
            )
        self.load_all_model_data(models)

    def load_all_model_data(self, models):
        # we load the data now based on the sorted order of our tables, so
        # we can load our foreign key dependencies properly
        for model_name in self.sort_models():
            # we won't be loading data for many-to-many relationships
            if model_name in models:
                logger.debug("Loading data for model: %s", model_name)
                model = models[model_name]
                model_data_path = os.path.join(self.data_path, model_name)
                if os.path.isdir(model_data_path):
                    self.load_model_data(model_data_path, model)
            else:
                logger.debug("Skipping loading data models for table: %s", model_name)

    def sort_models(self):
        """Sorts the database models appropriately based on their relationships so that we load our data
        in the appropriate order.

        Returns:
            A sorted list containing the names of the models.
        """
        model_names = [
            table.name for table in self.Base.metadata.sorted_tables if table.name in self.models
        ]
        logger.debug("Unsorted models: %s", model_names)
        model_count = len(model_names)

        swapped = True
        sort_round = 0
        while swapped:
            sort_round += 1
            logger.debug('Sorting round: %d (%s)', sort_round, model_names)

            sorted_models = []
            for i in range(model_count):
                model = self.models[model_names[i]]
                # check if this model has any dependencies which haven't been taken care of in this round
                for foreign_model_name in model.foreign_models:
                    if foreign_model_name not in sorted_models:
                        sorted_models.append(foreign_model_name)

                if model.name not in sorted_models:
                    sorted_models.append(model.name)

            # we're done here (no changes after this sorting round)
            if model_names == sorted_models:
                swapped = False

            model_names = sorted_models

        logger.debug("Sorted models: %s (%d rounds)", model_names, sort_round)
        return model_names

    def create_model_table(self, model):
        """Creates the table for the given model.

        Args:
            model: A StatikModel instance.

        Returns:
            A SQLAlchemy model instance for the table corresponding to this
            particular model.
        """
        try:
            return db_model_factory(self.Base, model, self.models)
        except Exception as exc:
            raise ModelError(
                model.name,
                message="failed to create in-memory table.",
                orig_exc=exc,
                context=self.error_context
            )

    def load_model_data(self, path, model):
        """Loads the data for the specified model from the given path.
        """
        if os.path.isdir(path):
            # try find a model data collection
            if os.path.isfile(os.path.join(path, '_all.yml')):
                self.load_model_data_collection(path, model)
            else:
                self.load_model_data_from_files(path, model)
            self.session.commit()

    def load_model_data_collection(self, path, model):
        full_filename = os.path.join(path, '_all.yml')
        self.error_context.update(filename=full_filename)

        db_model = globals()[model.name]
        # load the collection data from the collection file
        with open(full_filename, mode='rt', encoding=self.encoding) as f:
            collection = yaml.load(f.read())

        if not isinstance(collection, list):
            raise InvalidModelCollectionDataError(
                model.name,
                context=self.error_context
            )
        seen_entries = set()
        logger.debug("Loading %d instance(s) for model: %s", len(collection), model.name)
        for item in collection:
            if not isinstance(item, dict) or 'pk' not in item:
                raise InvalidModelCollectionDataError(
                    model.name,
                    context=self.error_context
                )

            entry = StatikDatabaseInstance(
                name=item['pk'],
                from_dict=item,
                model=model,
                session=self.session,
                encoding=self.encoding,
                markdown_config=self.markdown_config
            )
            # duplicate primary key!
            if entry.field_values['pk'] in seen_entries:
                raise DuplicateModelInstanceError(
                    model.name,
                    pk=entry.field_values['pk'],
                    context=self.error_context
                )
            else:
                seen_entries.add(entry.field_values['pk'])

            try:
                db_entry = db_model(**entry.field_values)
                self.session.add(db_entry)
            except Exception as exc:
                raise DataError(
                    model.name,
                    pk=entry.field_values['pk'],
                    message="failed to insert entry into in-memory database.",
                    orig_exc=exc,
                    context=self.error_context
                )
        
        self.error_context.clear()

    def load_model_data_from_files(self, path, model):
        db_model = globals()[model.name]
        entry_files = list_files(path, ['yml', 'yaml', 'md'])
        seen_entries = set()
        logger.debug("Loading %d instance(s) for model: %s", len(entry_files), model.name)
        for entry_file in entry_files:
            entry = StatikDatabaseInstance(
                filename=os.path.join(path, entry_file),
                model=model,
                session=self.session,
                encoding=self.encoding,
                markdown_config=self.markdown_config,
                error_context=self.error_context
            )
            # duplicate primary key!
            if entry.field_values['pk'] in seen_entries:
                raise DuplicateModelInstanceError(
                    model.name,
                    pk=entry.field_values['pk'],
                    context=self.error_context
                )
            else:
                seen_entries.add(entry.field_values['pk'])

            try:
                db_entry = db_model(**entry.field_values)
                self.session.add(db_entry)
            except Exception as exc:
                raise DataError(
                    model.name,
                    pk=entry.field_values['pk'],
                    message="failed to insert entry into in-memory database.",
                    orig_exc=exc,
                    context=self.error_context
                )

        self.error_context.clear()

    def query(self, query, additional_locals=None, safe_mode=False):
        """Executes the given SQLAlchemy query string.

        Args:
            query: The SQLAlchemy ORM query (or Python code) to be executed.
            additional_locals: Any additional local variables to inject into the execution context
                when executing the query.
            safe_mode: Boolean value indicating whether or not to execute queries in safe mode
                only. If True, this only allows MLAlchemy-style queries. If False, this allows
                both exec() and MLAlchemy-style queries. Default: False.

        Returns:
            The result of executing the query.
        """
        logger.debug("Attempting to execute database query: %s", query)

        if safe_mode and not isinstance(query, dict):
            raise SafetyViolationError(
                context=self.error_context
            )

        if isinstance(query, dict):
            logger.debug("Executing query in safe mode (MLAlchemy)")
            return mlalchemy.parse_query(query).to_sqlalchemy(self.session, self.tables).all()
        else:
            logger.debug("Executing unsafe query (Python exec())")
            if additional_locals is not None:
                for k, v in iteritems(additional_locals):
                    locals()[k] = v

            exec(
                compile(
                    'result = %s' % query.strip(),
                    '<string>',
                    'exec'
                ),
                globals(),
                locals()
            )
            return locals()['result']

    def shutdown(self):
        """Shuts down the database engine."""
        self.session.close_all()
        self.engine.dispose()
        # clear all tracked global variables
        clear_tracked_globals()


class StatikDatabaseInstance(ContentLoadable):

    def __init__(self, model=None, session=None, **kwargs):
        super(StatikDatabaseInstance, self).__init__(**kwargs)
        if model is None:
            raise MissingParameterError("model", context=self.error_context)
        self.model = model

        if session is None:
            raise MissingParameterError("session", context=self.error_context)
        self.session = session

        # convert the vars to their underscored representation
        self.field_values = underscore_var_names(self.vars)
        self.field_values['pk'] = self.name

        # run through the foreign key fields to check their assignment
        for field_name in self.model.field_names:
            field = self.model.fields[field_name]
            if isinstance(field, StatikDateTimeField) and \
                    isinstance(self.field_values.get(field_name), basestring):
                # attempt to perform an intelligent date/time parse operation
                self.field_values[field_name] = dateutil_parse(self.field_values[field_name])
            # if it's a foreign key
            elif isinstance(field, StatikForeignKeyField):
                # if we've got a pk value for a foreign key field
                if field_name in self.field_values:
                    self.field_values['%s_id' % field_name] = self.field_values[field_name]
                    del self.field_values[field_name]

            elif isinstance(field, StatikManyToManyField) and (field_name in self.field_values):
                if not isinstance(self.field_values[field_name], list):
                    raise InvalidFieldTypeError(
                        self.model.name,
                        field_name,
                        "a list",
                        context=self.error_context
                    )
                logger.debug(
                    "Attempting to look up primary keys for ManyToMany " +
                    "field relationship: %s", self.field_values[field_name]
                )
                # convert the list of field values to a query to look up the
                # primary keys of the corresponding table
                other_model = globals()[field.field_type]
                self.field_values[field_name] = self.session.query(
                    other_model
                ).filter(
                    other_model.pk.in_(self.field_values[field_name])
                ).all()

        # populate any Content field for this model
        if self.model.content_field is not None:
            self.field_values[self.model.content_field] = self.content

        logger.debug('%s', self)

    def __repr__(self):
        result = ["StatikDatabaseInstance(model=%s" % self.model.name]
        for field_name, field_value in iteritems(self.field_values):
            model_field = self.model.fields.get(field_name, None)
            if isinstance(model_field, StatikContentField) or isinstance(model_field, StatikTextField):
                result.append("%s=<...>" % field_name)
            else:
                result.append("%s=%s" % (field_name, field_value))
        result[-1] += ')'
        return ', '.join(result)

    def __str__(self):
        return repr(self)


def db_model_factory(Base, model, all_models):

    def get_or_create_association_table(model1_name, model2_name):
        _association_table_name = calculate_association_table_name(model1_name, model2_name)
        logger.debug("Creating/getting ManyToMany relationship table: %s", _association_table_name)
        if _association_table_name in globals():
            return globals()[_association_table_name]

        # create an association table
        _association_table = Table(
            _association_table_name,
            Base.metadata,
            Column('%s_pk' % model1_name.lower(), String, ForeignKey('%s.pk' % model1_name)),
            Column('%s_pk' % model2_name.lower(), String, ForeignKey('%s.pk' % model2_name))
        )
        # track it in our globals
        set_global(_association_table_name, _association_table)
        return _association_table

    logger.debug('-----')
    logger.debug("Generating model: %s", model.name)
    model_fields = {
        '__tablename__': model.name,
        'pk': Column(String, primary_key=True)
    }

    # populate all of the relevant additional relationships for this model
    for field_name, rel in iteritems(model.additional_rels):
        kwargs = {}
        if rel.get('back_populates', None) is not None:
            kwargs['back_populates'] = rel['back_populates']
        if rel.get('secondary', None) is not None:
            kwargs['secondary'] = get_or_create_association_table(*rel['secondary'])
        logger.debug(
            'Creating additional relationship %s.%s -> %s (%s)',
            model.name,
            field_name,
            rel['to_model'],
            kwargs
        )
        model_fields[field_name] = relationship(rel['to_model'], **kwargs)

    # now populate all of the standard fields
    for field_name in model.field_names:
        field = model.fields[field_name]
        if field.field_type in SQLALCHEMY_FIELD_MAPPER:
            # if it's a simple field
            model_fields[field.name] = Column(
                field.name,
                SQLALCHEMY_FIELD_MAPPER[field.field_type]
            )

        elif field.field_type in all_models:
            # if it's a foreign key reference
            if isinstance(field, StatikForeignKeyField):
                model_fields['%s_id' % field.name] = Column(
                    '%s_id' % field.name,
                    ForeignKey('%s.pk' % field.field_type)
                )
                # if it's a self-referencing foreign key
                if field.field_type == model.name:
                    back_populates = field.back_populates or 'children'
                    model_fields[back_populates] = relationship(
                        field.field_type,
                        backref=backref(field_name, remote_side=[model_fields['pk']])
                    )
                else:
                    kwargs = {}
                    if field.back_populates is not None:
                        kwargs['back_populates'] = field.back_populates
                        logger.debug('Field %s.%s has back-populates field name: %s',
                            model.name, field_name, field.back_populates
                        )
                    else:
                        logger.debug('No back-populates field name for %s.%s',
                            model.name, field_name
                        )

                    model_fields[field.name] = relationship(
                        field.field_type,
                        **kwargs
                    )

            elif isinstance(field, StatikManyToManyField):
                association_table = get_or_create_association_table(model.name, field.field_type)

                kwargs = {'secondary': association_table}
                if field.back_populates is not None:
                    kwargs['back_populates'] = field.back_populates

                logger.debug("Creating model ManyToMany field %s.%s -> %s (%s)",
                    model.name, field.name, field.field_type, kwargs
                )
                model_fields[field.name] = relationship(
                    field.field_type,
                    **kwargs
                )

        else:
            raise InvalidFieldTypeError(
                model.name,
                field.name
            )

    Model = type(
        str(model.name),
        (Base,),
        model_fields
    )

    logger.debug("Model %s fields = %s", model.name, model_fields)

    # add the model class reference to the global scope
    set_global(model.name, Model)
    return Model
