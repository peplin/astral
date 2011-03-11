"""
astral.bin.base
==========

Base class for command line utilities.

"""
import os
import sys

from optparse import OptionParser, make_option as Option

import astral.node


class Command(object):
    """Inspired by the Celery project's command line tools."""
    args = ''
    version = astral.__version__
    option_list = ()
    preload_options = (
            Option("-s", "--settings",
                    default="astralsettings", action="store",
                    dest="settings_module",
                    help="Name of the module to read settings from."),
    )

    Parser = OptionParser

    def __init__(self):
        self.node = astral.node.Node()

    def usage(self):
        return "%%prog [options] %s" % (self.args, )

    def get_options(self):
        return self.option_list

    def handle_argv(self, prog_name, argv):
        options, args = self.parse_options(prog_name, argv)
        settings_module = options.settings_module
        if settings_module:
            os.environ["ASTRAL_SETTINGS_MODULE"] = settings_module
        else:
            os.environ["ASTRAL_SETTINGS_MODULE"] = 'astral.conf.global_settings'
        return self.run(*args, **vars(options))

    def run(self, *args, **options):
        raise NotImplementedError("subclass responsibility")

    def execute_from_commandline(self, argv=None):
        if argv is None:
            argv = list(sys.argv)
        prog_name = os.path.basename(argv[0])
        return self.handle_argv(prog_name, argv[1:])

    def parse_options(self, prog_name, arguments):
        """Parse the available options."""
        # Don't want to load configuration to just print the version,
        # so we handle --version manually here.
        if "--version" in arguments:
            print(self.version)
            sys.exit(0)
        parser = self.create_parser(prog_name)
        options, args = parser.parse_args(arguments)
        return options, args

    def create_parser(self, prog_name):
        return self.Parser(prog=prog_name,
                           usage=self.usage(),
                           version=self.version,
                           option_list=(self.preload_options +
                                        self.get_options()))
