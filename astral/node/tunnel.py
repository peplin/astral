import threading
import asyncore

from astral.net.tunnel import Tunnel
from astral.models import Ticket

import logging
log = logging.getLogger(__name__)


class TunnelControlThread(threading.Thread):
    def __init__(self):
        super(TunnelControlThread, self).__init__()
        self.daemon = True
        self.tunnels = dict()

    def run(self):
        asyncore.loop()

    def create_tunnel(self, ticket_id, source_ip, source_port,
            destination_ip, destination_port):
        tunnel = Tunnel(source_ip, source_port, destination_ip,
                destination_port)
        log.info("Starting %s", tunnel)
        self.tunnels[ticket_id] = tunnel

    def destroy_tunnel(self, ticket_id):
        tunnel = self.tunnels.pop(ticket_id)
        log.info("Stopping %s", tunnel)
        tunnel.close()

    def open_new_tunnels(self):
        for ticket in Ticket.query.all():
            if ticket.id not in self.tunnels:
                self.create_tunnel(ticket.source.ip_address, ticket.source_port,
                        ticket.destination.ip_address, ticket.destination_port)

    def close_expired_tunnels(self):
        for ticket_id, tunnel in self.tunnels.values():
            if not Ticket.get_by(id=ticket_id):
                self.destroy_tunnel(ticket_id)
