# Statik Change Log

This is the **Statik** change log as of version `0.6.0`.

## Release History

### `v0.16.0` - 01 February 2017

* Enhanced templating engine, allowing for more pluggable template
  system support.
* Added support for [Mustache](http://mustache.github.io/) templates.
* Now forcing Mustache templating in safe mode.

### `v0.15.0` - 30 January 2017

* Adding support for
  [MLAlchemy](https://github.com/thanethomson/MLAlchemy)-style queries.
* Adding support for **safe mode**, which only allows for
  MLAlchemy-style queries.

### `v0.14.3` - 23 January 2017

* Now allowing project's `assets` and `templates` folders to
  override themes' corresponding folders.
* Optimising asset copying process while watching project for changes
  (**Statik** now only copies files that have been modified or do not
  yet exist in the destination assets folder).
* Bumping minimum version dependency for `httpwatcher` to v0.5.0.

### `v0.14.2` - 18 January 2017

* `v0.14.1` fix didn't fix `README.rst` file inclusion issue. Attempting
  another fix.

### `v0.14.1` - 18 January 2017

* Minor tweak to setup script to fix inclusion of `README.rst` file.

### `v0.14.0` - 18 January 2017

* Replacing [livereload](https://github.com/lepture/python-livereload)
  dependency with
  [httpwatcher](https://github.com/thanethomson/httpwatcher).
* Adding ability to automatically open web browser when server starts
  up (and to turn it off).

### `v0.13.0` - 12 January 2017

* Adding Lorem Ipsum generator Markdown and Jinja extensions.

### `v0.12.0` - 10 January 2017

* Adding support for permalinking during Markdown processing.
* Fixing bug where theme-based project generation uses old `assets`
  folder instead of theme's `assets` folder.
* Fixing bug where folder watching doesn't work for themed projects.

### `v0.11.1` - 10 January 2017

* Now testing with Python 3.6 as well.

### `v0.11.0` - 10 January 2017

* Added support for themes.

### `v0.10.4` - 27 December 2016

* For pagination: forcing `Page.has_previous()` and `Page.has_next()`
  results to `bool`.
* Turned `Page.has_previous` and `Page.has_next` into properties.

### `v0.10.3` - 27 December 2016

* For pagination: bugfix for incorrect iteration.

### `v0.10.2` - 27 December 2016

* For pagination: minor fix for reverse lookup of paginated URLs.

### `v0.10.1` - 27 December 2016

* For pagination: added ability to manually specify the starting
  page number.

### `v0.10.0` - 26 December 2016

* Added pagination functionality for simplified pagination.
* Minor tweak to check that path templates are indeed strings.

### `v0.9.1` - 23 December 2016

* Changed **Statik** dependency versions to look for minimum versions of
  packages, as per #33.

### `v0.9.0` - 07 December 2016

* Adding `toc`, `footnotes` and `tables` extensions to Markdown
  parser.

### `v0.8.1` - 21 November 2016

* Minor bugfix to apply encoding to output files as well.

### `v0.8.0` - 21 November 2016

* Adding support for Python 2.7+

### `v0.7.1` - 21 November 2016

* Adding traceback to exception logging

### `v0.7.0` - 24 October 2016

* Merged pull request #29 - Add 'encoding' config option to allow / force
  opening files with a specific encoding

### `v0.6.7` - 01 September 2016

* Fixing issue #28 - trailing comma issue (which only seems to come up with Python 3.4 for some reason).

### `v0.6.6` - 09 August 2016

* Fixing issue #26 - now allowing for overlapping simple and complex views.

### `v0.6.5` - 28 July 2016

* Now allowing pretty much any name as a field name for Statik models (i.e. you can now use `name` as a valid
  field name).

### `v0.6.4` - 18 July 2016

* Yet another bugfix with regard to non-standard config file path (need more unit tests for this).
* Updating SQLAlchemy dependency to latest version (1.0.14).

### `v0.6.3` - 15 July 2016

* More bugfixes with regard to non-standard config file path.

### `v0.6.2` - 15 July 2016

* Fixing another bug in watcher code to do with non-standard configuration (facepalm here).

### `v0.6.1` - 15 July 2016

* Fixing bug in watcher code with non-standard configuration file.
* Now stripping extraneous whitespace from context variables.

### `v0.6.0` - 15 July 2016

* Added ability to specify project configuration YAML file explicitly. This allows for different project-wide
  configurations, such as for cases when one wants separate configurations for dev/QA/production. Allows for
  better automated builds.
