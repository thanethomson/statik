======
Statik
======

**Statik** aims to be a simple, yet powerful, generic static web site generator.
Instead of forcing you to adhere to a particular data structure/model (like the
standard blog data model, with posts, pages and tags),
**Statik** allows you to define your own data models in YAML format, and
instances of those data models either in YAML or Markdown. This is all loaded
into an in-memory SQLAlchemy_ SQLite database when rendering your *views*.

Then, code up your templates using the Jinja2_ templating engine (very similar
to the Django templating engine).

Finally, define your *views* (either complex or simple) in YAML format,
telling **Statik** how to render your data and templates to specific URLs for
your shiny new static web site. Write queries for your views in SQLAlchemy's
ORM_ syntax to make your life easier.

See the repository_  and the wiki_ for more details.

.. _SQLAlchemy: http://www.sqlalchemy.org/
.. _Jinja2: http://jinja.pocoo.org/
.. _ORM: http://docs.sqlalchemy.org/en/rel_1_0/orm/tutorial.html
.. _repository: https://github.com/thanethomson/statik
.. _wiki: https://github.com/thanethomson/statik/wiki
