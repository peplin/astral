#!/usr/bin/env python
"""astralnode

.. program:: astralnode

.. cmdoption:: -s, --settings

    Path to Astral node settings file 

"""
from optparse import make_option as Option

from astral.bin.base import Command
from astral.node import Node

class NodeCommand(Command):
    namespace = "astralnode"
    enable_config_from_cmdline = True
    supports_args = False

    def run(self, *args, **kwargs):
        self.node = Node(**kwargs)
        self.node.run()

    def get_options(self):
        settings = self.node.settings
        return (
            Option('-s', '--settings',
                default=settings.ASTRAL_SETTINGS_MODULE,
                action="store", dest="settings_module",
                help="Name of the settings module to import"),
        )

def main():
    pass

if __name__ == "__main__":
    main()
