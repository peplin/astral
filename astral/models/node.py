from elixir import Entity, Field, Unicode, Integer

from astral.api.client import NodeAPI


class Node(Entity):
    ip_address = Field(Unicode(15))
    port = Field(Integer)
    rtt = Field(Integer)
    upstream = Field(Integer)
    downstream = Field(Integer)

    RTT_STEP = 0.2
    BANDWIDTH_STEP = 0.2

    @classmethod
    def from_json(cls, data):
        return cls(ip_address=data['ip_address'])

    def update_rtt(self):
        sampled_rtt = NodeAPI(self.uri()).ping()
        self.rtt = self._weighted_average(self.rtt, self.RTT_STEP, sampled_rtt)
        return self.rtt

    def update_downstream(self):
        byte_count, transfer_time = NodeAPI(self.uri()).downstream_check()
        self.downstream = self._weighted_average(self.downstream,
                self.BANDWIDTH_STEP, byte_count / transfer_time)
        return self.downstream

    def update_upstream(self):
        byte_count, transfer_time = NodeAPI(self.uri()).upstream_check()
        self.upstream = self._weighted_average(self.upstream,
                self.BANDWIDTH_STEP, byte_count / transfer_time)
        return self.upstream

    def _weighted_average(self, estimated, step, sample):
        if not estimated:
            return sample
        return (1 - step) * estimated + step * sample

    def uri(self):
        return "http://%s:%s" % (self.ip_address, self.port)

    def __repr__(self):
        return u'<Node %s>' % self.ip_address
