from tornado.httpclient import HTTPRequest
from nose.tools import eq_, ok_
import json
import faker

from astral.api.tests import BaseTest
from astral.models import Stream
from astral.models.tests.factories import StreamFactory

class StreamsHandlerTest(BaseTest):
    def test_get_streams(self):
        [StreamFactory() for _ in range(3)]
        response = self.fetch('/streams')
        eq_(response.code, 200)
        result = json.loads(response.body)
        ok_('streams' in result)
        for stream in result['streams']:
            ok_(Stream.get_by(name=stream['name']))

    def test_create_stream(self):
        data = {'name': faker.lorem.sentence()}
        eq_(Stream.get_by(name=data['name']), None)
        self.http_client.fetch(HTTPRequest(
            self.get_url('/streams'), 'POST', body=json.dumps(data)), self.stop)
        response = self.wait()
        eq_(response.code, 200)
        ok_(Stream.get_by(name=data['name']))
