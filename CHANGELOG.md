# Statik Change Log

This is the **Statik** change log as of version `0.6.0`.

## Release History

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
