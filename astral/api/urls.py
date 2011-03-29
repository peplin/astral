from handlers.nodes import NodesHandler 
from handlers.node import NodeHandler 
from handlers.streams import StreamsHandler
from handlers.stream import StreamHandler
from handlers.ping import PingHandler
from handlers.events import EventHandler
from handlers.ticket import TicketHandler
from handlers.tickets import TicketsHandler


url_patterns = [
    (r"/nodes", NodesHandler),
    (r"/node/(\d+)", NodeHandler),
    (r"/streams", StreamsHandler),
    (r"/stream/(\d+)", StreamHandler),
    (r"/stream/(\d+)/tickets", TicketsHandler),
    (r"/stream/(\d+)/ticket/(\d+)", TicketHandler),
    (r"/stream/(\d+)/ticket", TicketHandler),
    (r"/ping", PingHandler),
    (r"/events", EventHandler),
]
