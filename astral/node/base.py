"""
astral.node.base
==========

Node Base Class.

"""
import os
import warnings
from copy import deepcopy

from astral.datastructures import AttributeDict, ConfigurationView
from astral.exceptions import NotConfigured
from astral.node.defaults import DEFAULTS

DEFAULT_CONFIG_MODULE = "astralconfig"

DEFAULT_SETTINGS = {
    "DEBUG": False,
}

DEFAULT_UNCONFIGURED_SETTINGS = {
}


def wanted_module_item(item):
    return item[0].isupper() and not item.startswith("_")


class Node(object):
    def __init__(self, settings_module=None):
        pass

    def run(self, **kwargs):
        pass

    @property
    def conf(self):
        """Current configuration (dict and attribute access)."""
        if not hasattr(self, '_conf'):
            self._conf = ConfigurationView({}, [deepcopy(DEFAULTS)])
        return self._conf


    def setup_settings(self, settingsdict):
        return AttributeDict(DEFAULT_SETTINGS, **settingsdict)

    def read_configuration(self):
        """Read configuration from :file:`astralconfig.py` and configure
        astral and Django so it can be used by regular Python."""
        configname = os.environ.get("ASTRAL_CONFIG_MODULE",
                                    DEFAULT_CONFIG_MODULE)
        try:
            astralconfig = self.import_from_cwd(configname)
        except ImportError:
            warnings.warn(NotConfigured(
                "No %r module found! Please make sure it exists and "
                "is available to Python." % (configname, )))
            return self.setup_settings(DEFAULT_UNCONFIGURED_SETTINGS)
        else:
            usercfg = dict((key, getattr(astralconfig, key))
                            for key in dir(astralconfig)
                                if wanted_module_item(key))
            self.configured = True
            return self.setup_settings(usercfg)

    def config_from_object(self, obj, silent=False):
        """Read configuration from object, where object is either
        a real object, or the name of an object to import.

            >>> astral.config_from_object("myapp.astralconfig")

            >>> from myapp import astralconfig
            >>> astral.config_from_object(astralconfig)

        """
        del(self.conf)
        return self.config_from_object(obj, silent=silent)

    def config_from_envvar(self, variable_name, silent=False):
        """Read configuration from environment variable.

        The value of the environment variable must be the name
        of an object to import.

            >>> os.environ["ASTRAL_CONFIG_MODULE"] = "myapp.astralconfig"
            >>> astral.config_from_envvar("ASTRAL_CONFIG_MODULE")

        """
        del(self.conf)
        return self.config_from_envvar(variable_name, silent=silent)

    def config_from_cmdline(self, argv, namespace="astral"):
        """Read configuration from argv.

        The config

        """
        self.conf.update(self.cmdline_config_parser(argv, namespace))
