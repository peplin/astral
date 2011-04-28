#! /usr/bin/env python
"""
TCP Socket liaison/tunnel asyncore test for RTMP streaming

Source: http://code.activestate.com/recipes/483732/
"""
import socket, asyncore


class Tunnel(asyncore.dispatcher, object):
    """TCP packet forwarding tunnel as an asyncore channel.

    Forward TCP packets through a tunnel from source socket to another local
    socket, and vice versa. The "source" is the intial point of entry - this is
    where the connections get started. The destination is most likely the
    service you already have listening on a port somewhere, e.g. an RTMP server.

    """
    def __init__(self, source_ip, source_port, bind_ip='', bind_port=0,
            backlog=5, enabled=True):
        super(Tunnel, self).__init__()
        self.sender = None
        self.enabled = enabled
        self.source_ip = source_ip
        self.source_port = source_port
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((bind_ip, bind_port))
        self.listen(backlog)

    @property
    def bind_ip(self):
        return self.socket.getsockname()[0]

    @property
    def bind_port(self):
        return self.socket.getsockname()[1]

    def change_status(self, enabled):
        self.enabled = enabled
        if self.sender:
            self.sender.enabled = enabled
            self.sender.receiver.enabled = enabled

    def handle_accept(self):
        conn, addr = self.accept()
        self.sender = Sender(Receiver(conn, enabled=self.enabled),
                self.source_ip, self.source_port, enabled=self.enabled)

    def __str__(self):
        return "<Tunnel from %s:%s -> %s:%s>" % (self.source_ip,
                self.source_port, self.bind_ip, self.bind_port)


class Receiver(asyncore.dispatcher, object):
    def __init__(self, connection, enabled=True):
        super(Receiver, self).__init__(connection)
        self.from_remote_buffer = ''
        self.to_remote_buffer = ''
        self.sender = None
        self.enabled = enabled

    def handle_connect(self):
        pass

    def handle_read(self):
        read = self.recv(512)
        if self.enabled:
            self.from_remote_buffer += read

    def writable(self):
        return (len(self.to_remote_buffer) > 0)

    def handle_write(self):
        sent = self.send(self.to_remote_buffer)
        self.to_remote_buffer = self.to_remote_buffer[sent:]

    def handle_close(self):
        self.close()
        if self.sender:
            self.sender.close()


class Sender(asyncore.dispatcher, object):
    def __init__(self, receiver, destination_ip, destination_port,
            enabled=True):
        super(Sender, self).__init__()
        self.receiver = receiver
        receiver.sender = self
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((destination_ip, destination_port))
        self.enabled = enabled

    def handle_connect(self):
        pass

    def handle_read(self):
        read = self.recv(512)
        if self.enabled:
            self.receiver.to_remote_buffer += read

    def writable(self):
        return len(self.receiver.from_remote_buffer) > 0

    def handle_write(self):
        sent = self.send(self.receiver.from_remote_buffer)
        self.receiver.from_remote_buffer = self.receiver.from_remote_buffer[sent:]

    def handle_close(self):
        self.close()
        self.receiver.close()


if __name__=='__main__':
    publisher_address = ('127.0.0.1', 1935)
    liaison_address = ('127.0.0.1', 5000)
    Tunnel(liaison_address[0], liaison_address[1], publisher_address[0],
            publisher_address[1])
    print "Liaison started: %s:%d <-> %s:%d" % (publisher_address[0],
            publisher_address[1], liaison_address[0], liaison_address[1])
    asyncore.loop()
