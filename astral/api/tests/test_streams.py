from nose.tools import eq_, ok_
import json

from astral.api.tests import BaseTest
from astral.models.stream import Stream
from astral.models.tests.factories import StreamFactory

class StreamsHandlerTest(BaseTest):
    def test_get_streams(self):
        streams = [StreamFactory() for _ in range(3)]
        response = self.fetch('/streams')
        eq_(response.code, 200)
        result = json.loads(response.body)
        ok_('streams' in result)
        for stream in result['streams']:
            ok_(Stream.get_by(name=stream['name']))
