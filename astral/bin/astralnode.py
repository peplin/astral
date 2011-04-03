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
                action="store", dest="uuid",
                help="UUID override, for testing multiple nodes on one box"),
        )

def main():
    node = NodeCommand()
    node.execute_from_commandline()

if __name__ == "__main__":
    main()
