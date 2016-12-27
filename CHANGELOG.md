# Statik Change Log

This is the **Statik** change log as of version `0.6.0`.

## Release History

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
