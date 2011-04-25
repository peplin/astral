#! /usr/bin/env python
"""
TCP Socket liaison/tunnel asyncore test for RTMP streaming

Source: http://code.activestate.com/recipes/483732/
"""
import socket, asyncore


class Tunnel(asyncore.dispatcher, object):
    """TCP packet forwarding tunnel as an asyncore channel.

    Forward TCP packets through a tunnel from source to destination and vice
    versa. The "source" is the intial point of entry - this is where the
    connections get started. The destination is most likely the service you
    already have listening on a port somewhere, e.g. an RTMP server.

    """
    def __init__(self, destination_ip, destination_port, source_ip='',
            source_port=0, backlog=5):
        super(Tunnel, self).__init__()
        self.destination_ip = destination_ip
        self.destination_port = destination_port
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((source_ip, source_port))
        self.listen(backlog)

    @property
    def source_ip(self):
        return self.socket.getsockname()[0]

    @property
    def source_port(self):
        return self.socket.getsockname()[1]

    def handle_accept(self):
        conn, addr = self.accept()
        Sender(Receiver(conn), self.destination_ip, self.destination_port)

    def __str__(self):
        return "<Tunnel from %s:%s -> %s:%s>" % (self.source_ip,
                self.source_port, self.destination_ip, self.destination_port)


class Receiver(asyncore.dispatcher, object):
    def __init__(self, connection):
        super(Receiver, self).__init__(connection)
        self.from_remote_buffer = ''
        self.to_remote_buffer = ''
        self.sender = None
        self.enabled = True

    def handle_connect(self):
        pass

    def handle_read(self):
        read = self.recv(4096)
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
    def __init__(self, receiver, remoteaddr, destination_port):
        super(Sender, self).__init__()
        self.receiver = receiver
        receiver.sender = self
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((remoteaddr, destination_port))
        self.enabled = True

    def handle_connect(self):
        pass

    def handle_read(self):
        read = self.recv(4096)
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
