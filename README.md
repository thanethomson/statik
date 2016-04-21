# Statik

Copyright (c) 2016, Thane Thomson

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
TBC

## Installation
TBC

## Usage
TBC

## Project Structure
By default we refer to a single site's data and generated HTML content into a
*project*, and projects have a very specific structure. Your base project
structure should look similar to the following example.

```
config.json              - Overall configuration for the project

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
```
