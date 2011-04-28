import restkit
import json
import timeit
import random
import string

from astral.conf import settings
from astral.exceptions import NetworkError, NotFound

import logging
log = logging.getLogger(__name__)


class NodeAPI(restkit.Resource):
    def __init__(self, uri, **kwargs):
        kwargs.setdefault('timeout', 3)
        kwargs.setdefault('max_tries', 1)
        super(NodeAPI, self).__init__(uri, **kwargs)

    def make_headers(self, headers):
        return headers or {'Accept': 'application/json',
                'Content-Type': 'application/json'}

    def request(self, *args, **kwargs):
        try:
            response = super(NodeAPI, self).request(*args, **kwargs)
        except (restkit.RequestError, ValueError), e:
            raise NetworkError(e)
        else:
            body = response.body_string()
            if body and response.headers.get('Content-Type'
                    ) == "application/json":
                body = json.loads(body)
            response.body = body
            return response

    def ping(self):
        timer = timeit.Timer("NodeAPI('%s').get('/ping')" % self.uri,
                "from astral.api.client import NodeAPI")
        return timer.timeit(1)

    def downstream_check(self, byte_count=None):
        byte_count = byte_count or settings.DOWNSTREAM_CHECK_LIMIT
        timer = timeit.Timer("NodeAPI('%s').get('/ping', bytes=%s)"
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
    def list(self):
        response = self.get('/nodes')
        if response:
            return response.body['nodes']
        else:
            return []

    def register(self, payload=None):
        return self.post('/nodes', payload=json.dumps(payload))

    def unregister(self, node_url=None):
        if node_url == None:
           node_url = '/node'
        try:
            return self.delete(node_url)
        except NetworkError, e:
            log.warning("Can't connect to server: %s", e)


class StreamsAPI(NodeAPI):
    def find(self, slug):
        try:
            return self.get('/stream/%s' % slug).body['stream']
        except restkit.ResourceNotFound, e:
            raise NotFound(e)

    def list(self):
        return self.get('/streams').body['streams']

    def create(self, **kwargs):
        response = self.post('/streams', payload=json.dumps(kwargs))
        return response.status == 200

class TicketsAPI(NodeAPI):
    def create(self, tickets_url, destination_uuid=None):
        response = self.post(tickets_url, payload=json.dumps(
            {'destination_uuid': destination_uuid}))
        if response.status_int == 200 or response.status_int == 302:
            response = self.get(response.headers['Location'])
            return response.body['ticket']

    def list(self):
        return self.get('/tickets').body['tickets']

    def getticket(self,ticket_url):
        return self.get(ticket_url)

    def cancel(self, ticket_url):
        try:
            return self.delete(ticket_url)
        except NetworkError, e:
            log.warning("Can't connect to server: %s", e)

    def confirm(self, ticket_url):
        try:
            response = self.put(ticket_url, payload=json.dumps(
                {'confirmed': True}))
        except NetworkError:
            return False
        else:
            return response.status == 200


class RemoteIP(NodeAPI):
    def __init__(self):
        super(RemoteIP, self).__init__(settings.JSON_IP_SERVER)

    def get(self):
        return super(RemoteIP, self).get().body['ip']
