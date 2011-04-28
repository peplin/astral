import threading
import asyncore

from astral.conf import settings
from astral.net.tunnel import Tunnel
from astral.models import Ticket, Node, session, Stream
from astral.models.ticket import TUNNEL_QUEUE

import logging
log = logging.getLogger(__name__)


class TunnelControlThread(threading.Thread):
    def __init__(self):
        super(TunnelControlThread, self).__init__()
        self.daemon = True
        self.tunnels = dict()
        self.stream_tunnels = dict()
        self.async_loop_thread = TunnelLoopThread()

    def handle_ticket(self, ticket):
        # reload to get a new database session
        ticket = Ticket.get_by(id=ticket.id)
        if ticket.source == Node.me():
            source_ip = "127.0.0.1"
        else:
            source_ip = ticket.source.ip_address
        try:
            port = self.create_tunnel(ticket.id, source_ip,
                    ticket.source_port, self.tunnels)
        except Exception, e:
            log.warning("Couldn't create a tunnel for %s: %s",
                    ticket, e)
        else:
            if not ticket.destination_port or ticket.destination_port != port:
                ticket.destination_port = port
            session.commit()
            self.close_expired_tunnels()
        finally:
            TUNNEL_QUEUE.task_done()

    def _handle_stream(self, stream):
        """Update the enabled flag on all tunnels that are for this stream."""
        # reload to get a new database session
        stream = Stream.get_by(slug=stream.slug)
        try:
            port = self.create_tunnel(stream.slug, "127.0.0.1",
                    settings.RTMP_PORT, self.stream_tunnels)
        except Exception, e:
            log.warning("Couldn't create a tunnel for %s: %s",
                    stream, e)
        else:
            if not stream.source_port or stream.source_port != port:
                stream.source_port = port
            session.commit()
        self.close_expired_stream_tunnels()
        self.update_stream_tunnel_flags()
        TUNNEL_QUEUE.task_done()

    def update_stream_tunnel_flags(self):
        for slug, tunnel in self.stream_tunnels.items():
            stream = Stream.get_by(slug=slug)
            if stream:
                pass
                #log.debug("Set streaming status of %s to %s", tunnel,
                #stream.streaming)
                # TODO temporarily disabled, doesn't seem to work with RTMP
                #if tunnel.enabled != stream.streaming:
                    #tunnel.change_status(stream.streaming)

    def run(self):
        while True:
            obj = TUNNEL_QUEUE.get()
            log.debug("Found %s in tunnel queue", obj)
            if isinstance(obj, Ticket):
                self._handle_ticket(obj)
            elif isinstance(obj, Stream):
                self._handle_stream(obj)

    def create_tunnel(self, ticket_id, source_ip, source_port, tunnel_dict):
        tunnel = tunnel_dict.get(ticket_id)
        if not tunnel:
            tunnel = Tunnel(source_ip, source_port, enabled=True)
            log.info("Starting %s", tunnel)
            tunnel_dict[ticket_id] = tunnel
        else:
            log.info("Found existing %s", tunnel)
        if not self.async_loop_thread.running:
            self.async_loop_thread.start()
        return tunnel.bind_port

    def destroy_tunnel(self, key, tunnel_dict):
        tunnel = tunnel_dict.pop(key)
        log.info("Stopping %s", tunnel)
        tunnel.handle_close()

    def close_expired_tunnels(self):
        for ticket_id, tunnel in self.tunnels.items():
            if not Ticket.get_by(id=ticket_id):
                self.destroy_tunnel(ticket_id, self.tunnels)

    def close_expired_stream_tunnels(self):
        for slug, tunnel in self.stream_tunnels.items():
            if not Stream.get_by(slug=slug):
                self.destroy_tunnel(slug, self.stream_tunnels)


class TunnelLoopThread(threading.Thread):
    def __init__(self):
        super(TunnelLoopThread, self).__init__()
        self.daemon = True
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            asyncore.loop()
