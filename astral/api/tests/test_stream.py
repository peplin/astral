from nose.tools import eq_, ok_
import json

from astral.api.tests import BaseTest
from astral.models.tests.factories import StreamFactory
        

class StreamHandlerTest(BaseTest):
    def test_get_stream(self):
        stream = StreamFactory()
        response = self.fetch(stream.absolute_url())
        eq_(response.code, 200)
        result = json.loads(response.body)
        ok_('stream' in result)
        eq_(result['stream']['id'], stream.id)
        eq_(result['stream']['name'], stream.name)
