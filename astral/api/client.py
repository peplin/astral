import restkit
import json

from astral.conf import settings
from astral.exceptions import OriginWebserverError

class Nodes(restkit.Resource):
    def __init__(self, **kwargs):
        super(Nodes, self).__init__(settings.ASTRAL_WEBSERVER, **kwargs)

    def get(self, query=None):
        return super(Nodes, self).get('/nodes', query)

    def make_headers(self, headers):
        return headers or {'Accept': 'application/json'}

    def request(self, *args, **kwargs):
        try:
            response = super(Nodes, self).request(*args, **kwargs)
        except restkit.RequestError, e:
            raise OriginWebserverError(e)
        else:
            return json.loads(response.body_string())
