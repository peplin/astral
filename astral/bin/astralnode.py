#!/usr/bin/env python
"""astralnode

.. program:: astralnode

.. cmdoption:: -c, --config

    Path to Astral node config module 

"""
from optparse import make_option as Option

from astral.bin.base import Command

class NodeCommand(Command):
    namespace = "astralnode"
    enable_config_from_cmdline = True
    supports_args = False

    def run(self, *args, **kwargs):
        self.node.run(**kwargs)

    def get_options(self):
        conf = self.node.conf
        return (
            Option('-s', '--something',
                default=conf.ASTRAL_SOME_SETTING,
                action="store", dest="some_setting",
                help="A setting"),
        )

def main():
    node = NodeCommand()
    node.execute_from_commandline()

if __name__ == "__main__":
    main()
