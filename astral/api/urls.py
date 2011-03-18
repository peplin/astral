from handlers.nodes import NodesHandler 
from handlers.node import NodeHandler 
from handlers.streams import StreamsHandler
from handlers.stream import StreamHandler
from handlers.ping import PingHandler

url_patterns = [
    (r"/nodes", NodesHandler),
    (r"/node/(\d+)", NodeHandler),
    (r"/streams", StreamsHandler),
    (r"/stream/(\d+)", StreamHandler),
    (r"/ping", PingHandler),
]
