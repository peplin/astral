from handlers.nodes import NodesHandler 
from handlers.node import NodeHandler 
from handlers.streams import StreamsHandler
from handlers.stream import StreamHandler
from handlers.ping import PingHandler
from handlers.events import EventHandler
from handlers.ticket import TicketHandler
from handlers.tickets import TicketsHandler
from handlers.settings import SettingsHandler


url_patterns = [
    (r"/nodes", NodesHandler),
    (r"/node/(\d+)", NodeHandler),
    (r"/node", NodeHandler),
    (r"/streams", StreamsHandler),
    (r"/tickets", TicketsHandler),
    (r"/stream/(.+)/ticket/(\d+)", TicketHandler),
    (r"/stream/(.+)/tickets", TicketsHandler),
    (r"/stream/(.+)/ticket", TicketHandler),
    (r"/stream/(.+)", StreamHandler),
    (r"/ping", PingHandler),
    (r"/settings", SettingsHandler),
    (r"/events", EventHandler),
]
