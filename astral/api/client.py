import restkit
import json
import timeit

from astral.conf import settings
from astral.exceptions import OriginWebserverError


class NodeAPI(restkit.Resource):
    def __init__(self, uri, **kwargs):
        super(NodeAPI, self).__init__(uri, **kwargs)

    def make_headers(self, headers):
        return headers or {'Accept': 'application/json'}

    def request(self, *args, **kwargs):
        try:
            response = super(NodeAPI, self).request(*args, **kwargs)
        except restkit.RequestError, e:
            raise OriginWebserverError(e)
        else:
            return json.loads(response.body_string())

    def ping(self):
        timer = timeit.Timer("NodeAPI('%s').get('/ping')" % self.uri,
                "from astral.api.client import NodeAPI")
        return timer.timeit(1)

    def downstream_check(self, byte_count=None):
        byte_count = byte_count or settings.DOWNSTREAM_CHECK_LIMIT
        timer = timeit.Timer("NodeAPI('%s').get('/ping', {'bytes': %s})"
                % (self.uri, byte_count),
                "from astral.api.client import NodeAPI")
        return byte_count, timer.timeit(1)

    def upstream_check(self, byte_count=None):
        byte_count = byte_count or settings.UPSTREAM_CHECK_LIMIT
        payload = {}
        with open('/dev/random') as random_file:
            payload['bytes'] = random_file.read(byte_count)
        timer = timeit.Timer("NodeAPI('%s').post('/ping', payload=%s)"
                % (self.uri, json.dumps(payload)),
                "from astral.api.client import NodeAPI")
        return byte_count, timer.timeit(1)


class Nodes(NodeAPI):
    def get(self, query=None):
        return super(Nodes, self).get('/nodes', query)

class Streams(NodeAPI):
    def get(self, query=None):
        return super(Nodes, self).get('/streams', query)
