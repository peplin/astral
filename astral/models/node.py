from elixir import (Field, Unicode, Integer, Entity, Boolean,
        using_table_options, ManyToOne)
from elixir.events import after_insert
from sqlalchemy import UniqueConstraint
import uuid
import json

from astral.exceptions import RequestError
from astral.models.base import BaseEntityMixin
from astral.models.event import Event
from astral.api.client import NodeAPI, RemoteIP
from astral.conf import settings

import logging
log = logging.getLogger(__name__)


class Node(BaseEntityMixin, Entity):
    ip_address = Field(Unicode(15))
    uuid = Field(Unicode(64), nullable=False, unique=True, primary_key=True)
    port = Field(Integer)
    supernode = Field(Boolean, default=False)
    primary_supernode = ManyToOne('Node')
    rtt = Field(Integer)
    upstream = Field(Integer) # KB/s
    downstream = Field(Integer) # KB/s

    using_table_options(UniqueConstraint('ip_address', 'port'))

    API_FIELDS = ['ip_address', 'uuid', 'port', 'supernode',]
    RTT_STEP = 0.2
    BANDWIDTH_STEP = 0.2

    @classmethod
    def from_dict(cls, data):
        node = Node.get_by(uuid=data['uuid'])
        if not node:
            node = cls(ip_address=data['ip_address'], uuid=data['uuid'],
                    port=data['port'])
        if 'supernode' in data:
            node.supernode = data['supernode']
        if 'primary_supernode_uuid' in data:
            node.primary_supernode = Node.get_by(
                    uuid=data['primary_supernode_uuid'])
        return node

    def update_rtt(self):
        try:
            sampled_rtt = NodeAPI(self.uri()).ping()
        except RequestError:
            log.warning("Unable to connect to %s for updating RTT -- "
                    "leaving it at %s", self, self.rtt)
        else:
            self.rtt = self._weighted_average(self.rtt, self.RTT_STEP,
                    sampled_rtt)
        return self.rtt

    def update_downstream(self):
        byte_count, transfer_time = NodeAPI(self.uri()).downstream_check()
        self.downstream = self._weighted_average(self.downstream,
                self.BANDWIDTH_STEP, byte_count / transfer_time / 1000.0)
        return self.downstream

    def update_upstream(self, url=None):
        byte_count, transfer_time = NodeAPI(url or self.uri()).upstream_check()
        self.upstream = self._weighted_average(self.upstream,
                self.BANDWIDTH_STEP, byte_count / transfer_time / 1000.0)
        return self.upstream

    def _weighted_average(self, estimated, step, sample):
        if not estimated:
            return sample
        return (1 - step) * estimated + step * sample

    @classmethod
    def update_supernode_rtt(cls):
        for supernode in cls.query.filter_by(supernode=True).filter(
                Node.uuid != Node.me().uuid):
            try:
                supernode.update_rtt()
            except RequestError:
                supernode.delete()

    @classmethod
    def supernodes(cls):
        return cls.query.filter_by(supernode=True)

    @classmethod
    def closest_supernode(cls):
        closest = cls.supernodes().filter(Node.uuid != Node.me().uuid
                ).order_by('rtt').first()
        if not Node.me().supernode and not closest:
            log.warn("No supernodes in the database")
        return closest

    @classmethod
    def me(cls, uuid_override=None, refresh=False):
        desired_uuid = uuid_override or unicode(uuid.getnode())
        node = Node.get_by(uuid=desired_uuid)
        if not node:
            node = Node()
            node.uuid = desired_uuid
            log.info("Using %s for this node's unique ID", node.uuid)
        if refresh:
            try:
                node.ip_address = RemoteIP().get()
            except RequestError, e:
                log.debug("Couldn't connect to the web: %s", e)
                node.ip_address = '127.0.0.1'
            log.info("Using %s for this node's IP address", node.ip_address)

            node.port = settings.PORT
            log.info("Using %s for this node's API port", node.port)
        return node

    @classmethod
    def not_me(cls):
        return cls.query.filter(Node.uuid != Node.me().uuid).all()

    def uri(self):
        return "http://%s:%s" % (self.ip_address, self.port)

    def absolute_url(cls, uuid_override=''):
        """This class does a bit of double duty, as both a class and instance
        method. It's probably not great practice, but we'll try it out. The
        point is to have the URL pattern only be in one place.
        """
        if isinstance(cls, Node):
            uuid_override = uuid_override or cls.uuid
        return '/node/%s' % uuid_override

    def to_dict(self):
        data = super(Node, self).to_dict()
        if self.primary_supernode:
            data['primary_supernode_uuid'] = self.primary_supernode.uuid
        return data

    def conflicts_with(self, data):
        return (self.uuid != data['uuid'] and
                self.ip_address == data['ip_address'] and
                self.port == data['port'])

    @after_insert
    def emit_new_node_event(self):
        Event(message=json.dumps({'type': "node", 'data': self.to_dict()}))

    def __repr__(self):
        return u'<Node %s: %s:%s>' % (self.uuid, self.ip_address, self.port)
