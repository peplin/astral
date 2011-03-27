import logging
import logging.handlers

DEBUG = True

LOG_FORMAT = '[%(asctime)s: %(levelname)s] %(message)s'
if DEBUG:
    LOG_LEVEL = logging.DEBUG
else:
    LOG_LEVEL = logging.WARN
LOG_COLOR = True

PORT = 8000

TORNADO_SETTINGS = {}
TORNADO_SETTINGS['debug'] = DEBUG
TORNADO_SETTINGS['xsrf_cookies'] = False
TORNADO_SETTINGS['port'] = PORT

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
    'syslog_tag': "astral",
    'log_level': LOG_LEVEL,
    'use_syslog': USE_SYSLOG,
}

ASTRAL_WEBSERVER = "http://localhost:4567"
BOOTSTRAP_NODES = [
        {'ip_address': "127.0.0.1", 'port': 8001, 'uuid': '1', 'primary_supernode': 119779273282995},
        {'ip_address': "127.0.0.1", 'port': 8002, 'uuid': '2', 'primary_supernode': 119779273282995},
        {'ip_address': "127.0.0.1", 'port': 8003, 'uuid': '3', 'primary_supernode': 119779273282995},
        {'ip_address': "127.0.0.1", 'port': 8004, 'uuid': '4', 'primary_supernode': 119779273282995},
        {'ip_address': "127.0.0.1", 'port': 8005, 'uuid': '5', 'primary_supernode': 119779273282995},
        {'ip_address': "127.0.0.1", 'port': 8006, 'uuid': '6', 'primary_supernode': 119779273282995},
        {'ip_address': "127.0.0.1", 'port': 8007, 'uuid': '7', 'primary_supernode': 119779273282995},
        {'ip_address': "127.0.0.1", 'port': 8008, 'uuid': '8', 'primary_supernode': 119779273282995},
        {'ip_address': "127.0.0.1", 'port': 8009, 'uuid': '9', 'primary_supernode': 119779273282995},
        {'ip_address': "127.0.0.1", 'port': 8010, 'uuid': '10', 'primary_supernode': 119779273282995},
        {'ip_address': "127.0.0.1", 'port': 8011, 'uuid': '11', 'primary_supernode': 119779273282995},
        {'ip_address': "127.0.0.1", 'port': 8012, 'uuid': '12', 'primary_supernode': 119779273282995},
]

DOWNSTREAM_CHECK_LIMIT = 1024 * 1024 * 2
UPSTREAM_CHECK_LIMIT = 1024 * 256
