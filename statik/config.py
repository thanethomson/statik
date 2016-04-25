# -*- coding:utf-8 -*-
"""
Helper class for working with Statik configuration.
"""

import logging
import os.path

import utils
from errors import *

logger = logging.getLogger(__name__)
__all__ = [
    "StatikConfig",
]


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
        return self.get_string_opt(
            "projectName",
            default=os.path.basename(self._path),
        )


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
            _profiles = self._cfg['profiles']
            profiles = []
            for profile, _ in _profiles.iteritems():
                if not isinstance(profile, basestring):
                    raise InvalidConfigException("Profile name must be a string (%s)" % utils.pretty(profile))
                profiles.append(profile)

        return profiles


    def get_base_url(self):
        """Tries to get the base relative URL of the target site for the
        currently configured profile.

        Returns:
            A string containing the relative URL. Default: "/".
        """
        return self.get_string_opt("baseUrl", default="/")


    def get_output_path(self):
        """Attempts to get the output path for this project, into which the
        generated files will be saved.

        Returns:
            A string containing the absolute path into which the generated
            files will be saved. Defaults to: "[projectPath]/public/"
        """
        return utils.get_abs_path(
            self.get_string_opt(
                "outputPath",
                default="public",
            ),
            rel_base_path=self._path,
        )


    def get_assets_enabled(self):
        """Returns whether or not to enable the copying of assets.

        Returns:
            A boolean value.
        """
        return self.get_bool_opt(
            "assets.enabled",
            default=True,
        )


    def get_assets_source(self):
        """Attempts to find the source path for the assets for this project.
        This variable is profile-specific, so you can have different asset
        source paths for different build profiles.

        All files and subfolders will be copied as-is directly into the
        destination assets folder. See get_assets_dest().

        Returns:
            A string containing the absolute path to the source assets folder.
            Defaults to: "[projectPath]/assets/".
        """
        return utils.get_abs_path(
            self.get_string_opt(
                "assets.sourcePath",
                default="assets",
            ),
            rel_base_path=self._path,
        )


    def get_assets_dest(self):
        """Attempts to find the absolute destination path for where assets
        should be copied to. This variable is profile-specific, so you can have
        different asset destination paths for different build profiles.

        Returns:
            A string containing the absolute path to the destination assets
            folder. Defaults to: "[outputPath]/assets/".
        """
        return utils.get_abs_path(
            self.get_string_opt(
                "assets.destPath",
                default="assets",
            ),
            rel_base_path=self.get_output_path(),
        )


    def get_assets_recursive(self):
        """Retrieves the setting to indicate whether or not the asset copy
        should take place recursively.

        Returns:
            A boolean value indicating whether or not to copy the assets
            recursively. Defaults to True.
        """
        return self.get_bool_opt("assets.recursive", True)


    def get_assets_purge_dest(self):
        """Retrieves the setting to indicate whether or not to purge the
        assets' destination directory prior to copying.

        Returns:
            A boolean value indicating whether or not to purge the assets.
            Defaults to True.
        """
        return self.get_bool_opt("assets.purgeDest", True)


    def get_output_mode(self):
        """Attempts to get the output mode for this project.

        Returns:
            A string containing the output mode for this project. This can
            either be "standard" (the default), which renders URLs as
            "/path/to/url.html", or "pretty", which renders URLs as
            "/path/to/url/index.html".
        """
        return self.get_string_opt("outputMode", default="standard")


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


    def get_bool_opt(self, param, default=None):
        """Tries to retrieve the specified profile-aware parameter, checking
        that is is actually a boolean value.

        Args:
            param: The (string) name of the parameter to fetch.
            default: The default value of the parameter, if it cannot be found.

        Returns:
            The value of the requested boolean parameter.
        """
        val = self.get_opt(param, default=default)
        if not isinstance(val, bool):
            raise InvalidConfigException("Parameter \"%s\" is expected to be a boolean value" % param)
        return val


    def get_opt(self, param, default=None):
        """Attempts to get the value of the specified parameter from the
        configuration.

        Args:
            param: A dotted notation string indicating the path to the parameter
                value to be fetched, such as "param1" or "paramA.paramB.paramC".
            default: The default value of the parameter, if it cannot be found.

        Returns:
            The value of the requested parameter.
        """
        # break the parameter up into its parts
        param_list = param.split(".")
        val = None

        # try profile-specific config first
        if 'profiles' in self._cfg and \
            isinstance(self._cfg['profiles'], dict) and \
            self._profile in self._cfg['profiles'] and \
            isinstance(self._cfg['profiles'][self._profile], dict):
            val = self._search_for_opt(
                self._cfg['profiles'][self._profile],
                param_list,
            )

        # if we don't have a value yet
        if val is None:
            # try to find it in the global configuration
            val = self._search_for_opt(
                self._cfg,
                param_list,
            )

        # return the value or the default
        return val if val is not None else default


    def _search_for_opt(self, cfg, param_list):
        """Helper function to search for the specified parameter in the
        given configuration object.

        Args:
            cfg: A Python dictionary containing configuration information.
            param_list: The broken-down list of parameters for which to search
                in this configuration object. This will be performed
                recursively using this function.

        Returns:
            A parameter value, if found, or else None.
        """
        if not isinstance(cfg, dict) or param_list[0] not in cfg:
            return None

        if len(param_list) > 1:
            # search recursively
            return self._search_for_opt(cfg[param_list[0]], param_list[1:])

        # we found a value!
        return cfg[param_list[0]]
