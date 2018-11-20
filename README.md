# Statik

[![Build Status](https://travis-ci.org/thanethomson/statik.svg?branch=master)](https://travis-ci.org/thanethomson/statik)
[![PyPI](https://img.shields.io/pypi/v/statik.svg)](https://pypi.python.org/pypi/statik)
[![PyPI](https://img.shields.io/pypi/pyversions/statik.svg)](https://pypi.python.org/pypi/statik)

## Overview
**Statik** aims to be a simple, yet powerful, generic static web site generator.
Instead of forcing you to adhere to a particular data structure/model (like the
standard blog data model, with posts, pages and tags),
**Statik** allows you to define your own data models in YAML format, and
instances of those data models either in YAML or Markdown. This is all loaded
into an in-memory [SQLAlchemy](http://www.sqlalchemy.org/) SQLite database
when rendering your *views*.

Then, code up your templates using the [Jinja2](http://jinja.pocoo.org/)
templating engine (very similar to the Django templating engine), or
[Mustache](http://mustache.github.io/) templates.

Finally, define your *views* (either complex or simple) in YAML format,
telling **Statik** how to render your data and templates to specific URLs for
your shiny new static web site. Write queries for your views in SQLAlchemy's
[ORM syntax](http://docs.sqlalchemy.org/en/rel_1_0/orm/tutorial.html),
or [MLAlchemy](https://github.com/thanethomson/MLAlchemy) to make your
life easier.

See the [wiki](https://github.com/thanethomson/statik/wiki) for more details.

## Requirements
In order to install **Statik**, you will need:

* Python 2.7+ or Python 3.5+
* `pip` or `easy_install`

## Installation
Simply run the following:

```bash
> pip install statik
```
To upgrade, just run the following:

```bash
> pip install --upgrade statik
```

## Usage
To build the project in the current directory, writing output files to the
`public` directory within the current directory:

```bash
> statik
```

To build a project in another directory, writing output files to the
`public` directory within *that* directory:

```bash
> statik -p /path/to/project/folder
```

To build a project in another directory, with control over where to place the
output files:

```bash
> statik -p /path/to/project/folder -o /path/to/output/folder
```

## Project QuickStart
To create an empty project folder with the required project structure, simply run:

```bash
> statik -p /path/to/project/ --quickstart
```

## Statik Projects
A **Statik** project must adhere to the directory structure as follows:

```
config.yml    - YAML configuration file for the overall project.
assets/       - Static assets for the project (images, CSS files,
                scripts, etc.). Ignored if themes are used.
data/         - Instances for each of the different models, defined either in
                YAML or Markdown format.
models/       - A folder specifically dedicated to model definitions, in YAML
                format.
templates/    - Jinja2/Mustache template files. Ignored if themes are used.
templatetags/ - Python scripts defining custom Jinja2 template tags and
                filters.
themes/       - If your project uses themes, place them here. Each theme
                must be uniquely named, and must contain an "assets"
                and "templates" folder.
views/        - Configuration files, in YAML format, defining "recipes" for how
                to generate various different URLs (which models to use, which
                data and which templates).
```

For example projects, see the `examples` directory in the source repository.
For more information, see the [wiki](https://github.com/thanethomson/statik/wiki).

## Themes
Themes for **Statik** will slowly start appearing in the
[Statik Themes](https://github.com/thanethomson/statik-themes)
repository. Watch that space!

## Remote upload

**Statik** can publish your generated site for you through SFTP or through Netlify.

### SFTP
To publish your website on a server via SFTP, you can use the remote upload command 
line option. The connection parameters must be added to your project's `config.yml`.
 
```
remote:
    sftp:
        server: 'hostname or IP'
        dir-base: '/base/directory/'
        dir-root: 'relative/to/base/directory'  
        username: 'SSH username'
        password: 'SSH password'
```

### Netlify
To publish  your website via Netlify, you will need 2 things: 
your Netlify access token and your Netlify site id. 

First, specify your Netlify access token as an environment variable: 

Linux:

```bash
> export NETLIFY_TOKEN=<netlify_token>
```

Windows

```bash
> set NETLIFY_TOKEN=<netlify_token>
```

Then, run **Statik** by passing in `--upload=netlify` and your Netlify site id
`--netlify-site-id=<netlify_site_id>`. 

```bash
statik --upload=netlify --netlify-site-id=<netlify_site_id>
```
**Statik** will upload the static site that it outputs.

## License
**The MIT License (MIT)**

Copyright (c) 2016-2018 Thane Thomson

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
