# -*- coding:utf-8 -*-
"""
Helper class for working with Statik configuration.
"""

import logging
import os.path

import utils
from errors import *

logger = logging.getLogger(__name__)
__all__ = ["StatikConfig"]


class StatikConfig:
    """Encapsulates configuration for a Statik project."""

    def __init__(self, path, cfg, profile, default_profiles=['production']):
        """Constructor.

        Args:
            path: The full absolute file system path of the project.
            cfg: A Python dictionary containing the unprocessed configuration
                for a Statik project.
            profile: The name of the currently selected profile.
            default_profiles: A list of the possible profiles, if none are
                supplied in the configuration.
        """
        # make sure to remove any trailing slashes
        self._path = path.rstrip("/")
        self._cfg = cfg
        self._profile = profile
        self._default_profiles = default_profiles


    def get_project_name(self):
        """Retrieves the project's name.

        Returns:
            A string containing the name of the project.
        """
        return self._cfg.get('projectName', os.path.basename(self._path))


    def get_profiles(self):
        """Retrieves the profiles for this project.

        Returns:
            A list of strings containing the name(s) of the configured
            profile(s).

        Raises:
            InvalidConfigException: If a configuration option is invalid.
        """
        profiles = self._default_profiles

        if 'profiles' in self._cfg:
            profiles = self._cfg['profiles']
            if not isinstance(profiles, list):
                profiles = [profiles]
            for profile in profiles:
                if not isinstance(profile, basestring):
                    raise InvalidConfigException("Profile name must be a string (%s)" % utils.pretty(profile))

        return profiles


    def get_base_url(self):
        """Tries to get the base relative URL of the target site for the
        currently configured profile.

        Returns:
            A string containing the relative URL. Default: "/".
        """
        return self.get_string_opt("baseUrl", "/")


    def get_output_path(self):
        """Attempts to get the output path for this project, into which the
        generated files will be saved.

        Returns:
            A string containing the absolute path into which the generated
            files will be saved. Defaults to: "[projectPath]/public/"
        """
        return utils.get_abs_path(
            self.get_string_opt("outputPath",
            os.path.join(self._path, "public"))
        )


    def get_output_mode(self):
        """Attempts to get the output mode for this project.

        Returns:
            A string containing the output mode for this project. This can
            either be "standard" (the default), which renders URLs as
            "/path/to/url.html", or "pretty", which renders URLs as
            "/path/to/url/index.html".
        """
        return self._cfg.get("outputMode", "standard")


    def get_string_opt(self, param, default=None):
        """Tries to retrieve the specified profile-aware parameter, checking
        that it is actually a string.

        Args:
            param: The (string) name of the parameter to fetch.
            default: The default value of the parameter, if it cannot be found.

        Returns:
            The value of the requested string parameter.
        """
        val = self.get_opt(param, default=default)
        if not isinstance(val, basestring):
            raise InvalidConfigException("Parameter \"%s\" is expected to be a string" % param)
        return val


    def get_opt(self, param, default=None):
        """Generic function to get the value of a parameter from the config.

        Args:
            param: The (string) name of the parameter to fetch.
            default: The default value of the parameter, if it cannot be found.

        Returns:
            The value of the requested parameter.
        """
        # first check the per-profile configuration for the parameter
        if 'profileConfig' in self._cfg \
            and isinstance(self._cfg['profileConfig'], dict) \
            and self._profile in self._cfg['profileConfig'] \
            and isinstance(self._cfg['profileConfig'][self._profile], dict) \
            and param in self._cfg['profileConfig'][self._profile]:
            return self._cfg['profileConfig'][self._profile][param]

        # otherwise get the global-level parameter value
        return self._cfg.get(param, default)
