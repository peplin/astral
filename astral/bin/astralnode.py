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
            Option('-f', '--foobar',
                default="some value",
                action="store", dest="some_setting",
                help="A setting"),
        )

def main():
    node = NodeCommand()
    node.execute_from_commandline()

if __name__ == "__main__":
    main()
