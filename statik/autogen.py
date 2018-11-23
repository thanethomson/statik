import os.path

import yaml

from statik.config import *
from statik.fields import *
from statik.models import *
from statik.project import *
from statik.templating import *
from statik.utils import *

import logging
logger = logging.getLogger(__name__)

__all__ = ['autogen']

def autogen(project_path):
    """Autogenerates views and templates for all the models in the project."""
    generate_quickstart(project_path)

    project = StatikProject(project_path)
    project.config = StatikConfig(project.config_file_path)

    models = list(project.load_models().values())

    logger.info('Creating view and template for home page (index.html).')
    generate_yaml_file(os.path.join(project_path, StatikProject.VIEWS_DIR, 'index.yaml'),
                        {   
                            'path': '/',
                            'template': 'index'
                        }
    )
    generate_index_file(os.path.join(project_path, StatikProject.TEMPLATES_DIR, 'index.jinja2'))

    for model in models:
        logger.info('Creating view and template for model: %s' % model.name)
        generate_yaml_file(os.path.join(project_path, StatikProject.VIEWS_DIR, '%s.yaml' % model.name),
                            {   
                                'path': {
                                    'template': '/%s/{{ %s.pk }}' % (model.name, model.name),
                                    'for-each': {
                                        '%s' % model.name: 'session.query(%s).all()' % model.name
                                    }
                                },
                                'template': ('%s' % model.name),
                            }
        )
        generate_model_file(os.path.join(project_path, StatikProject.TEMPLATES_DIR, '%s.jinja2' % model.name),
                            project,
                            model,
                            model.fields.values())


def generate_yaml_file(filename, contents):
    """Creates a yaml file with the given content."""
    with open(filename, 'w') as file:
        file.write(yaml.dump(contents, default_flow_style=False))


def generate_index_file(filename):
    """Constructs a default home page for the project."""
    with open(filename, 'w') as file:
        content = open(os.path.join(os.path.dirname(__file__), 'templates/index_page.html'), 'r').read()
        file.write(content)


def generate_model_file(filename, project, model, fields):
    """Creates a webpage for a given instance of a model."""
    for field in fields:
        field.type = field.__class__.__name__

    content = open(os.path.join(os.path.dirname(__file__), 'templates/model_page.html'), 'r').read()

    engine = StatikTemplateEngine(project)
    template = engine.create_template(content)

    # create context and update from project.config
    context = {'model': model,
                'fields': fields}
    context.update(dict(project.config.context_static))
    string = template.render(context)

    with open(filename, 'w') as file:
        file.write(string)
