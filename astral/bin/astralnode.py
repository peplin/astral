#!/usr/bin/env python
"""astralnode

.. program:: astralnode

.. cmdoption:: -f, --foobar

    Path to Astral node config module 

"""
from optparse import make_option as Option

from astral.bin.base import Command

class NodeCommand(Command):
    def run(self, *args, **kwargs):
        self.node.run(**kwargs)

    def get_options(self):
        return (
            Option('-u', '--uuid',
                default=None,
                action="store", dest="uuid_override",
                help="UUID override, for testing multiple nodes on one box"),
            Option('-l', '--upstream-limit',
                default=None,
                action="store", dest="upstream_limit",
                help="Maximum upload bandwidth to use for forwarding streams"),
        )

def main():
    node = NodeCommand()
    node.execute_from_commandline()

if __name__ == "__main__":
    main()
