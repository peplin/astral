from elixir import Entity, Field, Unicode
  

class Node(Entity):
    ip_address = Field(Unicode(15))

    def from_json(cls, data):
        return cls(ip_address=data['ip_address'])

    def __repr__(self):
        return u'<Node %s>' % self.ip_address
