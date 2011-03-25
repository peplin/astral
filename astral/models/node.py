from elixir import Field, Unicode, Integer, Entity, Boolean, using_table_options
from sqlalchemy import UniqueConstraint
import uuid
import socket

from astral.models.base import BaseEntityMixin
from astral.api.client import NodeAPI
from astral.conf import settings

import logging
log = logging.getLogger(__name__)


class Node(BaseEntityMixin, Entity):
    ip_address = Field(Unicode(15), nullable=False)
    uuid = Field(Integer, nullable=False, unique=True)
    port = Field(Integer, nullable=False)
    supernode = Field(Boolean, nullable=False, default=False)
    rtt = Field(Integer)
    upstream = Field(Integer)
    downstream = Field(Integer)

    using_table_options(UniqueConstraint('ip_address', 'port'))

    RTT_STEP = 0.2
    BANDWIDTH_STEP = 0.2
    API_FIELDS = ['ip_address', 'uuid', 'port', 'supernode',]

    def __init__(self, *args, **kwargs):
        if not kwargs.get('uuid'):
            kwargs['uuid'] = uuid.getnode()
            log.info("Using %s for this node's unique ID", kwargs['uuid'])

        if not kwargs.get('ip_address'):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect((settings.ASTRAL_WEBSERVER, 80))
            except socket.gaierror, e:
                log.debug("Couldn't connect to the Astral webserver: %s", e)
                kwargs['ip_address'] = '127.0.0.1'
            else:
                kwargs['ip_address'] = s.getsockname()
            log.info("Using %s for this node's IP address", kwargs['ip_address'])

        if not kwargs.get('port'):
            kwargs['port'] = settings.PORT
            log.info("Using %s for this node's API port", kwargs['port'])

        return super(Node, self).__init__(*args, **kwargs)

    @classmethod
    def from_dict(cls, data):
        node = Node.get_by(uuid=data['uuid'])
        if not node:
            node = cls(ip_address=data['ip_address'], uuid=data['uuid'],
                    port=data['port'], supernode=data.get('supernode', False))
        return node

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

    def absolute_url(self):
        return '/node/%s' % self.uuid

    def to_dict(self):
        return dict(((field, getattr(self, field))
                for field in self.API_FIELDS))

    def __repr__(self):
        return u'<Node %s:%d>' % (self.ip_address, self.port)
