"""An extended version of the log_settings module from zamboni:
https://github.com/jbalogh/zamboni/blob/master/log_settings.py
"""
from tornado.options import _LogFormatter as TornadoLogFormatter
import tornado.options
import sys
import logging, logging.handlers
import os.path
import types

# For pretty log messages, if available
try:
    import curses
except:
    curses = None

import dictconfig

# Pulled from commonware.log we don't have to import that, which drags with
# it Django dependencies.
class RemoteAddressFormatter(logging.Formatter):
    """Formatter that makes sure REMOTE_ADDR is available."""

    def format(self, record):
        if ('%(REMOTE_ADDR)' in self._fmt
                and 'REMOTE_ADDR' not in record.__dict__):
            record.__dict__['REMOTE_ADDR'] = None
        return logging.Formatter.format(self, record)

class UTF8SafeFormatter(RemoteAddressFormatter):
    def __init__(self, fmt=None, datefmt=None, encoding='utf-8'):
        logging.Formatter.__init__(self, fmt, datefmt)
        self.encoding = encoding
    
    def formatException(self, e):
        r = logging.Formatter.formatException(self, e)
        if type(r) in [types.StringType]:
            r = r.decode(self.encoding, 'replace') # Convert to unicode
        return r
    
    def format(self, record):
        t = RemoteAddressFormatter.format(self, record)
        if type(t) in [types.UnicodeType]:
            t = t.encode(self.encoding, 'replace')
        return t

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

def initialize_logging(log_config):
    use_syslog = log_config.pop('use_syslog', False)
    log_level = log_config.pop('log_level', logging.INFO)
    syslog_tag = log_config.pop('syslog_tag')
    syslog_facility = log_config.pop('syslog_facility',
            logging.handlers.SysLogHandler.LOG_LOCAL0)

    if os.path.exists('/dev/log'):
        syslog_device = '/dev/log'
    elif os.path.exists('/var/run/syslog'):
        syslog_device = '/var/run/syslog'

    base_fmt = ('%(name)s:%(levelname)s %(message)s')

    cfg = {
        'version': 1,
        'filters': {},
        'formatters': {
            'debug': {
                '()': UTF8SafeFormatter,
                'datefmt': '%H:%M:%s',
                'format': '%(asctime)s ' + base_fmt,
            },
            'prod': {
                '()': UTF8SafeFormatter,
                'datefmt': '%H:%M:%s',
                'format': '%s: [%%(REMOTE_ADDR)s] %s' % (syslog_tag, base_fmt),
            },
            'tornado': {
                '()': TornadoLogFormatter,
                'color': True
            },
        },
        'handlers': {
            'console': {
                '()': logging.StreamHandler,
                'formatter': 'tornado'
            },
            'null': {
                '()': NullHandler,
            },
            'syslog': {
                '()': logging.handlers.SysLogHandler,
                'facility': syslog_facility,
                'address': syslog_device,
                'formatter': 'prod',
            },
        },
        'loggers': {
            # root logger
            '': {}
        }
    }

    for key, value in log_config.items():
        cfg[key].update(value)

    # Set the level and handlers for all loggers.
    for logger in cfg['loggers'].values():
        if 'handlers' not in logger:
            logger['handlers'] = ['syslog' if use_syslog else 'console']
        if 'level' not in logger:
            logger['level'] = log_level
        if 'propagate' not in logger:
            logger['propagate'] = False

    # Set up color if we are in a tty and curses is installed
    cfg['formatters']['tornado']['color'] = False
    if curses and sys.stderr.isatty():
        try:
            curses.setupterm()
            if curses.tigetnum("colors") > 0:
                cfg['formatters']['tornado']['color'] = True
        except:
            pass

    dictconfig.dictConfig(cfg)
