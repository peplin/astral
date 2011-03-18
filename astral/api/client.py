import restkit
import json

from astral.exceptions import OriginWebserverError


class NodeAPI(restkit.Resource):
    def __init__(self, base_url, **kwargs):
        super(NodeAPI, self).__init__(base_url, **kwargs)

    def make_headers(self, headers):
        return headers or {'Accept': 'application/json'}

    def request(self, *args, **kwargs):
        try:
            response = super(Nodes, self).request(*args, **kwargs)
        except restkit.RequestError, e:
            raise OriginWebserverError(e)
        else:
            return json.loads(response.body_string())

    def ping(self):
        return self.get('/ping')


class Nodes(restkit.Resource):
    def get(self, query=None):
        return super(Nodes, self).get('/nodes', query)

class Streams(restkit.Resource):
    def get(self, query=None):
        return super(Nodes, self).get('/streams', query)
