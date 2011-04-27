import threading
import asyncore

from astral.net.tunnel import Tunnel
from astral.models import Ticket, Node, session
from astral.models.ticket import TUNNEL_QUEUE

import logging
log = logging.getLogger(__name__)


class TunnelControlThread(threading.Thread):
    def __init__(self):
        super(TunnelControlThread, self).__init__()
        self.daemon = True
        self.tunnels = dict()
        self.async_loop_thread = TunnelLoopThread()

    def run(self):
        while True:
            ticket_id = TUNNEL_QUEUE.get()
            if not self.async_loop_thread.running:
                self.async_loop_thread.start()
            ticket = Ticket.get_by(id=ticket_id)
            log.debug("Found %s in tunnel queue", ticket)
            if ticket.source == Node.me():
                source_ip = "127.0.0.1"
            else:
                source_ip = ticket.source.ip_address
            port = self.create_tunnel(ticket.id, source_ip, ticket.source_port)
            TUNNEL_QUEUE.task_done()
            if not ticket.destination_port or ticket.destination_port != port:
                ticket.destination_port = port
            session.commit()
            self.close_expired_tunnels()

    def create_tunnel(self, ticket_id, source_ip, source_port):
        tunnel = self.tunnels.get(ticket_id)
        if not tunnel:
            tunnel = Tunnel(source_ip, source_port)
            log.info("Starting %s", tunnel)
            self.tunnels[ticket_id] = tunnel
        else:
            log.info("Found existing %s", tunnel)
        return tunnel.bind_port

    def destroy_tunnel(self, ticket_id):
        tunnel = self.tunnels.pop(ticket_id)
        log.info("Stopping %s", tunnel)
        tunnel.handle_close()

    def close_expired_tunnels(self):
        for ticket_id, tunnel in self.tunnels.items():
            if not Ticket.get_by(id=ticket_id):
                self.destroy_tunnel(ticket_id)


class TunnelLoopThread(threading.Thread):
    def __init__(self):
        super(TunnelLoopThread, self).__init__()
        self.daemon = True
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            asyncore.loop()
