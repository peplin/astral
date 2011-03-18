from elixir import Entity, Field, Unicode, Integer
import timeit


class Node(Entity):
    ip_address = Field(Unicode(15))
    port = Field(Integer)
    rtt = Field(Integer)

    RTT_STEP = 0.2

    @classmethod
    def from_json(cls, data):
        return cls(ip_address=data['ip_address'])

    def update_rtt(self):
        timer = timeit.Timer("NodeAPI('%s').ping()" % self.uri(),
                "from astral.api.client import NodeAPI")
        sampled_rtt = timer.timeit(1)
        if not self.rtt:
            self.rtt = sampled_rtt
        else:
            self.rtt = ((1 - self.RTT_STEP) * self.rtt
                    + self.RTT_STEP * sampled_rtt)
        return self.rtt

    def uri(self):
        return "%s:%s" % (self.ip_address, self.port)

    def __repr__(self):
        return u'<Node %s>' % self.ip_address
