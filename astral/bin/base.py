"""
astral.bin.base
==========

Base class for command line utilities.

"""
import os
import sys

from optparse import OptionParser, make_option as Option

import astral


class Command(object):
    """Inspired by the Celery project's command line tools."""
    args = ''
    version = astral.__version__
    option_list = ()
    supports_args = True
    enable_config_from_cmdline = False
    namespace = "astral"
    preload_options = (
            Option("--config",
                    default="astralconfig", action="store",
                    dest="config_module",
                    help="Name of the module to read configuration from."),
    )

    Parser = OptionParser

    def __init__(self, node=None, get_node=None):
        self.node = node
        self.get_node = get_node or self._get_default_node

    def usage(self):
        return "%%prog [options] %s" % (self.args, )

    def get_options(self):
        return self.option_list

    def handle_argv(self, prog_name, argv):
        options, args = self.parse_options(prog_name, argv)
        if not self.supports_args and args:
            sys.stderr.write(
                "\nUnrecognized command line arguments: %r\n" % (
                    ", ".join(args), ))
            sys.stderr.write("\nTry --help?\n")
            sys.exit(1)
        return self.run(*args, **vars(options))

    def run(self, *args, **options):
        raise NotImplementedError("subclass responsibility")

    def execute_from_commandline(self, argv=None):
        if argv is None:
            argv = list(sys.argv)
        argv = self.setup_node_from_commandline(argv)
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

    def setup_node_from_commandline(self, argv):
        preload_options = self.parse_preload_options(argv)
        node = (preload_options.pop("node", None) or
               os.environ.get("ASTRAL_NODE") or
               self.node)
        config_module = preload_options.pop("config_module", None)
        if config_module:
            os.environ["ASTRAL_CONFIG_MODULE"] = config_module
        if node:
            self.node = self.get_cls_by_name(node)
        else:
            self.node = self.get_node()
        if self.enable_config_from_cmdline:
            argv = self.process_cmdline_config(argv)
        return argv

    def parse_preload_options(self, args):
        acc = {}
        preload_options = dict((opt._long_opts[0], opt.dest)
                                for opt in self.preload_options)
        for arg in args:
            if arg.startswith('--') and '=' in arg:
                key, value = arg.split('=', 1)
                dest = preload_options.get(key)
                if dest:
                    acc[dest] = value
        return acc

    def get_cls_by_name(self, name):
        from astral.utils import get_cls_by_name, import_from_cwd
        return get_cls_by_name(name, imp=import_from_cwd)

    def process_cmdline_config(self, argv):
        try:
            cargs_start = argv.index('--')
        except ValueError:
            return argv
        argv, cargs = argv[:cargs_start], argv[cargs_start + 1:]
        self.node.config_from_cmdline(cargs, namespace=self.namespace)
        return argv

    def _get_default_node(self, *args, **kwargs):
        return astral.node.Node(*args, **kwargs)
