from nose.tools import eq_
from tornado.httpclient import HTTPRequest
import json
import random
import string
from urllib import urlencode

from astral.api.tests import BaseTest

class PingHandlerTest(BaseTest):
    def test_ping(self):
        response = self.fetch('/ping')
        eq_(response.code, 200)

    def test_downstream_check(self):
        response = self.fetch('/ping?%s' % urlencode({'bytes': 42}))
        eq_(response.code, 200)

    def test_upstream_check(self):
        payload = {}
        payload['bytes'] = ''.join((random.choice(string.ascii_letters)
                for _ in range(100)))
        self.http_client.fetch(HTTPRequest(self.get_url('/ping'), 'POST',
            body=json.dumps(payload)), self.stop)
        response = self.wait()
        eq_(response.code, 200)
