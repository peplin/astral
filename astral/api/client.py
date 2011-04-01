import restkit
import json
import timeit
import random
import string

from astral.conf import settings
from astral.exceptions import NetworkError


class NodeAPI(restkit.Resource):
    def __init__(self, uri, **kwargs):
        super(NodeAPI, self).__init__(uri, **kwargs)

    def make_headers(self, headers):
        return headers or {'Accept': 'application/json',
                'Content-Type': 'application/json'}

    def request(self, *args, **kwargs):
        try:
            response = super(NodeAPI, self).request(*args, **kwargs)
        except restkit.RequestError, e:
            raise NetworkError(e)
        else:
            body = response.body_string()
            if body and response.headers.get('Content-Type'
                    ) == "application/json":
                return json.loads(body)
            return body

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
        payload['bytes'] = ''.join((random.choice(string.ascii_letters)
                for _ in range(byte_count)))
        timer = timeit.Timer("NodeAPI('%s').post('/ping', payload=%s)"
                % (self.uri, json.dumps(payload)),
                "from astral.api.client import NodeAPI")
        return byte_count, timer.timeit(1)


class NodesAPI(NodeAPI):
    def list(self, query=None):
        return super(NodesAPI, self).get('/nodes', query)

    def register(self, payload=None):
        return super(NodesAPI, self).post('/nodes', payload=json.dumps(payload))

    def unregister(self, node):
        return super(NodesAPI, self).delete(node.absolute_url())


class StreamsAPI(NodeAPI):
    def list(self, query=None):
        return super(StreamsAPI, self).get('/streams', query)


class TicketsAPI(NodeAPI):
    def create(self, tickets_url, destination_uuid=None):
        response = super(TicketsAPI, self).post(tickets_url, payload=json.dumps(
            {'destination_uuid': destination_uuid}))
        return response.status == 200
