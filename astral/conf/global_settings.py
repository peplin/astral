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

if DEBUG:
    ASTRAL_WEBSERVER = "http://localhost:4567"
    DATABASE_PATH = ":memory:"
else:
    ASTRAL_WEBSERVER = "http://astral-video.heroku.com"
    DATABASE_PATH = "db"

BOOTSTRAP_NODES = [
]

DOWNSTREAM_CHECK_LIMIT = 1024 * 1024 * 2
UPSTREAM_CHECK_LIMIT = 1024 * 256

OUTGOING_STREAM_LIMIT = 2
UNCONFIRMED_TICKET_EXPIRATION = 1

RTMP_PORT = 1935
RTMP_TUNNEL_PORT = 5000
RTMP_APP_NAME = "astral"
