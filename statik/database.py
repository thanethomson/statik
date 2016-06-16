# -*- coding:utf-8 -*-

import os.path

from sqlalchemy import MetaData, String, Integer, Column, Table, ForeignKey, \
    Boolean, DateTime, Text, create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

from statik.common import ContentLoadable
from statik.fields import *
from statik.errors import *
from statik.utils import *

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


class StatikDatabase(object):

    def __init__(self, data_path, models):
        """Constructor.

        Args:
            data_path: The full path to where the database files can be found.
            models: Loaded model/field data.
        """
        self.data_path = data_path
        self.models = models
        self.engine = create_engine('sqlite:///:memory:')
        self.Base = declarative_base()
        self.session = sessionmaker(bind=self.engine)()
        globals()['session'] = self.session
        self.create_db(models)

    def create_db(self, models):
        """Creates the in-memory SQLite database from the model
        configuration."""
        # first create the table definitions
        self.tables = dict([(model_name, self.create_model_table(model)) for model_name, model in models.items()])
        # now create the tables in memory
        self.Base.metadata.create_all(self.engine)
        self.load_all_model_data(models)

    def load_all_model_data(self, models):
        # we load the data now based on the sorted order of our tables, so
        # we can load our foreign key dependencies properly
        for table in self.Base.metadata.sorted_tables:
            model_name = table.name
            model = self.models[model_name]
            model_data_path = os.path.join(self.data_path, model_name)
            if os.path.isdir(model_data_path):
                self.load_model_data(model_data_path, model)

    def create_model_table(self, model):
        """Creates the table for the given model.

        Args:
            model: A StatikModel instance.

        Returns:
            A SQLAlchemy model instance for the table corresponding to this
            particular model.
        """
        return db_model_factory(self.Base, model, self.models)

    def load_model_data(self, path, model):
        """Loads the data for the specified model from the given path.
        """
        if os.path.isdir(path):
            db_model = globals()[model.name]
            entry_files = list_files(path, ['yml', 'yaml', 'md'])
            seen_entries = set()
            for entry_file in entry_files:
                entry = StatikDatabaseInstance(
                    os.path.join(path, entry_file),
                    model=model
                )
                db_entry = db_model(**entry.field_values)
                self.session.add(db_entry)

            self.session.commit()

    def query(self, query):
        """Executes the given SQLAlchemy query string."""
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


class StatikDatabaseInstance(ContentLoadable):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'model' not in kwargs:
            raise MissingParameterError("Missing parameter \"model\" for database instance constructor")
        self.model = kwargs['model']

        # convert the vars to their underscored representation
        self.field_values = underscore_var_names(self.vars)
        self.field_values['pk'] = self.name

        # run through the foreign key fields to check their assignment
        for field_name in self.model.field_names:
            if isinstance(getattr(self.model, field_name), StatikForeignKeyField):
                # if we've got a pk value for a foreign key field
                if field_name in self.field_values:
                    self.field_values['%s_id' % field_name] = self.field_values[field_name]
                    del self.field_values[field_name]

        # populate any Content field for this model
        if self.model.content_field is not None:
            self.field_values[self.model.content_field] = self.content


def db_model_factory(Base, model, all_models):
    model_fields = {
        '__tablename__': model.name,
        'pk': Column(String, primary_key=True)
    }

    for field_name in model.field_names:
        field = getattr(model, field_name)
        if field.field_type in SQLALCHEMY_FIELD_MAPPER:
            # if it's a simple field
            model_fields[field.name] = Column(
                field.name,
                SQLALCHEMY_FIELD_MAPPER[field.field_type]
            )

        elif field.field_type in all_models:
            # if it's a foreign key reference
            model_fields['%s_id' % field.name] = Column(
                '%s_id' % field.name,
                ForeignKey('%s.pk' % field.field_type)
            )
            model_fields[field.name] = relationship(field.field_type)

        else:
            raise InvalidFieldTypeError("Unsupported database field type: %s" % field.field_type)

    Model = type(
        model.name,
        (Base,),
        model_fields
    )

    # add the model class reference to the global scope
    globals()[model.name] = Model
    return Model
