import restkit
import json
import timeit

from astral.conf import settings
from astral.exceptions import OriginWebserverError


class NodeAPI(restkit.Resource):
    def __init__(self, base_uri, **kwargs):
        super(NodeAPI, self).__init__(base_uri, **kwargs)

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
        timer = timeit.Timer("NodeAPI('%s').get('/ping')" % self.base_uri,
                "from astral.api.client import NodeAPI")
        return timer.timeit(1)

    def downstream_check(self, byte_count=None):
        byte_count = byte_count or settings.BANDWIDTH_CHECK_SIZE_LIMIT
        timer = timeit.Timer("NodeAPI('%s').get('/ping', {'bytes': %s})"
                % (self.base_uri, byte_count),
                "from astral.api.client import NodeAPI")
        return byte_count, timer.timeit(1)


class Nodes(NodeAPI):
    def get(self, query=None):
        return super(Nodes, self).get('/nodes', query)

class Streams(NodeAPI):
    def get(self, query=None):
        return super(Nodes, self).get('/streams', query)
