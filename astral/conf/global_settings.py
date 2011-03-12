import logging

DEBUG = False

LOG_FORMAT = '[%(asctime)s: %(levelname)s] %(message)s'
LOG_LEVEL = logging.WARN
LOG_COLOR = True

TORNADO_SETTINGS = {}
TORNADO_SETTINGS['debug'] = DEBUG
TORNADO_SETTINGS['xsrf_cookies'] = False

SYSLOG_TAG = "boilerplate"
SYSLOG_FACILITY = logging.handlers.SysLogHandler.LOG_LOCAL2

if DEBUG:
    LOG_LEVEL = logging.DEBUG
else:
    LOG_LEVEL = logging.INFO
USE_SYSLOG = False

LOGGING_CONFIG = 'astral.conf.logconfig.initialize_logging'
LOGGING = {
   'loggers': {
        'astral': {},
    },
    'syslog_facility': logging.handlers.SysLogHandler.LOG_LOCAL0,
    'syslog_tag': "bueda",
    'log_level': LOG_LEVEL,
    'use_syslog': USE_SYSLOG,
}
