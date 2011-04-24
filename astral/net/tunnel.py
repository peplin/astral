#! /usr/bin/env python
"""
TCP Socket liaison/tunnel asyncore test for RTMP streaming

Source: http://code.activestate.com/recipes/483732/
"""
import socket, asyncore


class Tunnel(asyncore.dispatcher, object):
    def __init__(self, ip, port, remote_ip, remote_port, backlog=5):
        super(Tunnel, self).__init__()
        self.remote_ip = remote_ip
        self.remote_port = remote_port
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((ip, port))
        self.listen(backlog)

    def handle_accept(self):
        conn, addr = self.accept()
        Sender(Receiver(conn), self.remote_ip, self.remote_port)

    def __str__(self):
        return "<Tunnel from %s:%s -> %s:%s>" % (self.source_ip,
                self.source_port, self.destination_ip, self.destination_port)


class Receiver(asyncore.dispatcher, object):
    def __init__(self, connection):
        super(Receiver, self).__init__(connection)
        self.from_remote_buffer = ''
        self.to_remote_buffer = ''
        self.sender = None

    def handle_connect(self):
        pass

    def handle_read(self):
        read = self.recv(4096)
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
    def __init__(self, receiver, remoteaddr, remote_port):
        super(Sender, self).__init__()
        self.receiver = receiver
        receiver.sender = self
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((remoteaddr, remote_port))

    def handle_connect(self):
        pass

    def handle_read(self):
        read = self.recv(4096)
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
