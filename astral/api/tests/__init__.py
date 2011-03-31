import tornado.testing

from astral.api.app import NodeWebAPI
from astral.models import drop_all, setup_all, create_all, session


class BaseTest(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return NodeWebAPI()

    def get_http_port(self):
        return 8000

    def setUp(self):
        super(BaseTest, self).setUp()
        setup_all()
        create_all()

    def tearDown(self):
        super(BaseTest, self).tearDown()
        session.commit()
        drop_all()
