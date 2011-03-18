import tornado.testing

from astral.api.app import NodeWebAPI


class BaseTest(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return NodeWebAPI()

    def get_http_port(self):
        return 8000
