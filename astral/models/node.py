from elixir import Entity, Field, Unicode
  

class Node(Entity):
    ip_address = Field(Unicode(15))

    def __repr__(self):
        return u'<Node %s>' % self.ip_address
