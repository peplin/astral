from nose.tools import eq_, ok_
from tornado.httpclient import HTTPRequest
import json

from astral.api.tests import BaseTest
from astral.models.tests.factories import StreamFactory
from astral.models import session
        

class StreamHandlerTest(BaseTest):
    def test_get_stream(self):
        stream = StreamFactory()
        response = self.fetch(stream.absolute_url())
        eq_(response.code, 200)
        result = json.loads(response.body)
        ok_('stream' in result)
        eq_(result['stream']['slug'], stream.slug)
        eq_(result['stream']['name'], stream.name)

    def test_resume_stream(self):
        stream = StreamFactory()
        session.commit()
        data = {'streaming': True}
        eq_(stream.streaming, False)
        self.http_client.fetch(HTTPRequest(
            self.get_url(stream.absolute_url()), 'PUT', body=json.dumps(data)),
            self.stop)
        response = self.wait()
        eq_(response.code, 200)
        eq_(stream.streaming, True)
