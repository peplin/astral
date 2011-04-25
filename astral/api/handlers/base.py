import json
import tornado.web
import tornado.websocket
from tornado import escape
from tornado.web import _utf8

import logging
logger = logging.getLogger('boilerplate.' + __name__)


class BaseHandler(tornado.web.RequestHandler):
    """A class to collect common handler methods - all other handlers should
    subclass this one.
    """

    def is_localhost(self):
        return self.request.remote_ip == "127.0.0.1"

    def load_json(self):
        """Load JSON from the request body and store them in
        self.request.arguments, like Tornado does by default for POSTed form
        parameters.

        If JSON cannot be decoded, raises an HTTPError with status 400.
        """
        if self.request.body:
            try:
                self.request.arguments = json.loads(self.request.body)
            except ValueError:
                msg = "Could not decode JSON: %s" % self.request.body
                logger.debug(msg)
                raise tornado.web.HTTPError(400, msg)

    def get_json_argument(self, name, default=None):
        """Find and return the argument with key 'name' from JSON request data.
        Similar to Tornado's get_argument() method.
        """
        if default is None:
            default = self._ARG_DEFAULT
        if not self.request.arguments:
            self.load_json()
        if name not in self.request.arguments:
            if default is self._ARG_DEFAULT:
                msg = "Missing argument '%s'" % name
                logger.debug(msg)
                raise tornado.web.HTTPError(400, msg)
            logger.debug("Returning default argument %s, as we couldn't find "
                    "'%s' in %s" % (default, name, self.request.arguments))
            return default
        arg = self.request.arguments[name]
        logger.debug("Found '%s': %s in JSON arguments" % (name, arg))
        return arg

    def write(self, chunk):
        """Patched version of Tornado's write that uses the correct content type
        'application/json', not 'text/javascript'.
        """
        assert not self._finished
        if isinstance(chunk, dict):
            chunk = escape.json_encode(chunk)
            self.set_header("Content-Type", "application/json")
            callback = self.get_argument('callback', None)
            if callback:
                chunk = "%s(%s)" % (callback, chunk)
        chunk = _utf8(chunk)
        self._write_buffer.append(chunk)

    def options(self, *args, **kwargs):
        """Insecure, just allows cross-origin requests for all handlers."""
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods",
                "POST, DELETE, OPTIONS, PUT, GET")
        self.set_header("Access-Control-Allow-Headers", "X-Requested-With")
        self.set_header("Access-Control-Max-Age", "180")


class BaseWebSocketHandler(tornado.websocket.WebSocketHandler, BaseHandler):
    pass
