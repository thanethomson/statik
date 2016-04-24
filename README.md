# Statik

[![PyPI version 0.1.0](https://img.shields.io/badge/pypi-v0.1.0-blue.svg)](https://pypi.python.org/pypi/statik/0.1.0)

## Overview
**Statik** aims to be a simple, yet powerful, static web site generator. It
is currently designed with developers in mind, and, unlike most other static
web site generators, is *not* geared towards building blogs by default.

Before you begin, make sure you know your HTML (especially
[Jinja2](http://jinja.pocoo.org/) templates),
[Markdown](https://en.wikipedia.org/wiki/Markdown) and
[JSON](https://en.wikipedia.org/wiki/JSON). If you really want to get fancy
with your site, you can learn some
[SQL](https://en.wikipedia.org/wiki/SQL) - specifically the
[SQLite](https://en.wikipedia.org/wiki/SQLite) dialect.

## Dependencies
You will need the following to be able to install Statik:

* Some kinds of POSIX-based OS, or Mac OS (Windows support will eventually be
  included, but right now it will break due to the way that Statik handles
  file system paths)
* Python 2.7.x (Python 3 support will come once Jinja2's Python 3 support
  graduates from being experimental)
* `virtualenv` if you want to run the code in a virtual environment or want
  to contribute to the development.

## Virtual Environment
If you don't want to install this package globally (perhaps you're using
Python 3 globally, but have to use Python 2 to run Statik), do the following:

```bash
> cd /path/to/your/desired/virtualenv
> virtualenv -p python27 .
> source bin/activate
```

The above makes the assumption that your Python 2.7.x interpreter's
executable file is called `python27` and is available on the path. The last
line (`source bin/activate`) activates the virtual environment. Now you're
free to run your Python 2.7 in a sandboxed environment, installing whatever
dependencies you want, and they won't interfere with your global
dependencies.

If you want to deactivate the virtual environment, simply just:

```bash
> deactivate
```

## Installation
### From PyPI
The quickest way to get up and running with Statik is by installing it from
PyPI. It's still recommended though to install it from within a virtual
environment, especially since it is currently only in `alpha`.

```bash
> pip install statik
```

### From Source
Once you've got your virtual environment working, check out this
repository and run the `setup.py` script:

```bash
> cd /path/to/where/you/want/it
> git clone https://github.com/thanethomson/statik.git
> cd statik/
> python setup.py install
```

This should install Statik into your virtual environment, and will automatically
install all of its Python dependencies too. It will also install a script,
`statik`, whose usage is as follows.

## Usage
### Command Line
Running the Statik script from the command line is easy:

```bash
> statik
```

That assumes that you want to build the project in the current folder. If you
want to build a project in a different folder, simply run:

```bash
> statik -p /path/to/your/project/folder
# or
> statik --project /path/to/your/project/folder
```

For help (doesn't give you any more than this right now), run:

```bash
> statik --help
```

### From Code
If you want to embed Statik in your own Python application, simply import the
`StatikProject` class and use as follows:

```python
from statik import StatikProject

# tell Statik where to find the project
project = StatikProject("/path/to/project/to/build")
# execute the build
project.build()
```

For more fine-grained control, see the source, which is relatively
well-documented.

## Project Structure
By default we refer to a single site's data and generated HTML content into a
*project*, and projects have a very specific structure. Your base project
structure should look similar to the following example.

```
config.json              - Global configuration for the project

models/                  - Data models (i.e. classes) are stored here
models/Post.json         - Structure definition for the "Post" class
models/Page.json         - Structure definition for the "Page" class
models/Author.json       - Structure definition for the "Author" class

data/                    - Data for the various models (i.e. instances) are stored here
data/Post/               - Instances of the "Post" class
data/Post/myfirstpost.md - An instance of the "Post" class
data/Page/               - Instances of the "Page" class
data/Page/home.md        - Instance of the "Page" class for the home page
data/Page/about.md       - Instance of the "Page" class for the about page
data/Author/             - Instances of the "Author" class
data/Author/michael.md   - Instance of the "Author" class for user "Michael"

templates/               - Jinja2 templates
templates/base.html      - Example base HTML template file
templates/header.html    - Example partial template
templates/footer.html    - Example partial template

views/                   - View configuration, connecting your templates, models and data
views/home.json          - Home page configuration
views/pages.json         - Configuration for our pages
views/posts.json         - Configuration for posts
views/authors.json       - Configuration for authors

assets/                  - Any files that are to be copied as-is into your destination project's "assets" folder
```

### Global Configuration
The global `config.json` file contains settings relevant to the overall
functioning of your generated site. The following fields are standard:

```js
{
  // String containing the global, human-readable name of your project.
  "projectName": "My project",

  // A list of strings containing the names of different kinds of execution
  // profiles for your project. This allows you to override certain settings
  // depending on which profile it is you're building for.
  // Default: ["production"]
  "profiles": ["dev", "prod"],

  // The output mode for generating URL paths. Can be one of:
  // "standard" - Generates URLs like /posts/2016/04/02/my-first-post.html
  // "pretty"   - Generates URLs like /posts/2016/04/02/my-first-post/index.html
  // Default: "standard"
  "outputMode": "pretty",

  // The base URL from which your site will eventually be served. This is
  // important, because sometimes web sites can be served from different
  // base paths to the root of the web server (e.g. http://site.com/basepath/
  // instead of http://site.com/). Statik generates URL references in your
  // templates in a relative manner, and this base URL will always be prefixed
  // to all generated URLs in the output.
  "baseUrl": "/",

  // Either a relative or absolute path in which to generate the output
  // HTML content. Default: [project path]/public/
  "outputPath": "./public/",

  // This object allows us to override certain facets of our configuration
  // depending on the selected profile for which we're building the site.
  // The global configuration values that can be overridden are:
  // baseUrl, outputPath
  "profileConfig": {
    // Configuration
    "dev": {
      // Overrides the previous "baseUrl" and "outputPath" settings
      "baseUrl": "/dev/",
      "outputPath": "./dev/public/"
    }
  }
}
```

### Models
Data models are defined in JSON files (with a `.json` extension). Each separate
JSON file in the `models/` folder of your project represents a single model,
analagous to a "class". Models simply contain key/value pairs indicating
their field names and field types.

#### Example Model: `Person.json`
```js
{
  "firstName": "string",
  "lastName": "string",
  "email": "string",
  "created": "datetime"
}
```

#### Example Model: `Post.json`
```js
{
  "title": "string",
  "slug": "string",
  // This author field is a foreign key reference to an instance of the
  // Person class, pointing, by default, to the "id" field of that class.
  "author": "fk|Person",
  "draft": "int",
  "content": "content",
  "published": "datetime"
}
```

#### Field Types
The following field types are available at present, and have their
equivalent SQLite and Python data types:

| Field Type | Description | SQLite | Python |
| ---------- | ----------- | ------ | ------ |
| `string` | Text | `TEXT` | `unicode` |
| `int` | Signed integer | `INT` | `int` |
| `date` | A date object, with year, month and day info | `DATE` | `datetime.date` |
| `datetime` | Similar to the date object, but with more detailed timestamp information | `DATETIME` | `datetime.datetime` |
| `float` | A floating-point number | `DOUBLE` | `float` |
| `content` | A special instance of `string` that receives Markdown content if data is specified in Markdown | `TEXT` | `unicode` |
| `fk` | A foreign key to another model instance | `TEXT` | N/A |

#### Primary Keys
Each model is automatically given an `id` field of type `TEXT` which is used
as its primary key. This is automatically assigned for instances of models
(see the section on **Data** next).

#### Foreign Keys
When specifying a field as a foreign key to another model, the source class'
field, by default, is created as a `TEXT` field, because the default
auto-generated `id` field for a class is of type `TEXT`. This allows us to
create instances that refer to other instances, simply by way of their
filename.

#### Content Fields
Each model may contain at most one field of the `content` type. Ultimately,
HTML content is stored in this field. If a class instance is written in
Markdown format, the Markdown content outside of the

### Data
Data instances are either defined in JSON or Markdown files (with `.json`,
`.md` or `.markdown` file extensions). The `data/` folder is primarily comprised
of subfolders - each one representing a specific model, as defined in the
`models/` folder.

The name of the file, without its extension, is used as the **primary key** or
`id` field value for the model instance.

#### Example Data: `michael.json`
Following on from our `Person` model example earlier, we could have an instance
named `michael.json`, whose primary key (`id` field) will be `michael`:

```js
{
  "firstName": "Michael",
  "lastName": "Anderson",
  "email": "manderson@gmail.com",
  // Under the hood, Statik uses Python's dateutil library for parsing date/time
  // values. See https://dateutil.readthedocs.org/en/stable/
  "created": "2016-04-22 14:04"
}
```

#### Example Data: `my-first-post.md`
The following instance of a `Post` object shows how one can construct a
post using Markdown, with a JSON *preamble* containing the relevant
metadata to populate the remaining fields of the post.

```markdown
===
{
  "title": "My first post!",
  "slug": "my-first-post",
  "author": "michael",
  "draft": 0,
  "published": "2016-04-22 14:30"
}
===

# Welcome
Welcome to Michael's first post!

## Here's a sub-heading
This content is written in Markdown format. It will automatically be parsed,
converted into HTML, and inserted as the value of the first field in
the `Post` model of type `content` (which, happens to be the field named
`content`).
```

### Templates
Templates are specified using [Jinja2](http://jinja.pocoo.org/docs/dev/)
syntax, which is very similar to [Django's](https://www.djangoproject.com/)
templating syntax. Templates are defined as HTML files (file extension
`.html`) within the `templates/` directory of your project.

#### Context
When rendering your templates, a context is present, depending on the
configuration of the **view** that refers to your template. This allows you
to pass variables and class instance data into your template for rendering.
See the documentation on **views** for more details.

#### Filters
Only the following basic filters are supplied at present. Custom filter
support is planned for a future release of Statik. These are invoked using
[standard Jinja 2 filter syntax](http://jinja.pocoo.org/docs/dev/templates/#filters).

* `date`: Converts a variable of type `date` or `datetime` into a string using
  the supplied format. Argument: an `strptime`/`strftime` format specifier. See
  the [`strftime()` and `strptime()` Behavior](https://docs.python.org/2/library/datetime.html#strftime-strptime-behavior)
  documentation.
* `slug`: Converts the supplied parameter into a slug (all lowercase, with
  special characters and spaces replaced by dashes). For example, the string
  `Hello world!` will be converted into the slug `hello-world`.

### Views
Views are the glue that hold your templates and data together. They define
which templates to render for which of your web site's paths, and what
data to supply to those templates. Views are stored in JSON format
(with extension `.json`) in your project's `views/` directory.

#### Example: `home.json`
An example home page, which simply renders a basic template and supplies that
template with the data of the latest 10 posts (ordered from most recent to
least), is shown as follows.

```js
{
  // Render /index.html
  "path": "/",
  // Find the template called "home.html" in the "templates/" directory.
  "template": "home.html",
  // Context data, whose contents will be supplied into the "home.html"
  // template during rendering.
  "data": {
    // The "title" variable will be supplied as-is to the template.
    "title": "Welcome to my blog",
    // The "posts" variable will first be recognised as an object, and if the
    // special "$" field is present, Statik will know to first execute that
    // as a SQL query to fetch the data to populate this field. Returned rows
    // from the SQL query will be converted into Python dictionaries,
    // where the "fields" parameter below indicates the order in which Statik
    // can expect the relevant field names.
    "posts": {
      "$": "SELECT id, slug, published, title, author, content FROM Post WHERE draft=0 ORDER BY published DESC LIMIT 10",
      "fields": ["id", "slug", "published", "title", "author", "content"]
    }
  }
}
```

#### Example: `posts.json`
When, for example, we want to automatically render all of the instances of the
`Post` class at different URLs, we can supply a view as follows.

```js
{
  // This is a model-based view, referring specifically to the "Post" model.
  "model": "Post",
  // Path specs are supplied as Jinja2 templates. When rendering, all of the
  // fields will be select from the specified model, and by default, all
  // instances of the model will be selected. This path spec is recomputed
  // for each instance of the model rendered. By default, the instance is
  // passed into the path spec template, where its variable is named according
  // to its model name. For example, an instance of the "Post" class will
  // be called "post"; an instance of the "Person" class will be called
  // "person"; an instance of another class called "MusicGenre" will be
  // called "musicGenre" (using camelCase).
  "path": "/{{ post.published|date('%Y/%m/%d') }}/{{ post.slug }}",
  // Uses the "fullpost.html" template file in the templates/ directory.
  "template": "fullpost.html"
}
```

## License
**The MIT License (MIT)**

Copyright (c) 2016 Thane Thomson

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
