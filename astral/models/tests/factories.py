import factory
import faker
import random
import uuid

from astral.conf import settings
from astral.models.base import slugify
from astral.models.stream import Stream
from astral.models.node import Node
from astral.models.ticket import Ticket


ELIXIR_CREATION = lambda class_to_create, **kwargs: class_to_create(**kwargs)
factory.Factory.set_creation_function(ELIXIR_CREATION)


class StreamFactory(factory.Factory):
    name = factory.LazyAttribute(lambda a: ' '.join(faker.lorem.words()))
    # TODO this does happen automatically, but we're not committing after every
    # factory object is created because of all of the sqlalchemy errors we get.
    # one day, we'll figure that shit out.
    slug = factory.LazyAttribute(lambda a: slugify(a.name))
    source = factory.LazyAttribute(lambda a: NodeFactory())


class NodeFactory(factory.Factory):
    ip_address = factory.LazyAttribute(lambda a: faker.internet.ip_address())
    uuid = factory.LazyAttribute(
            lambda a: unicode(random.randrange(1000, 1000000)))
    port = factory.LazyAttribute(lambda a: random.randrange(1000, 10000))

class SupernodeFactory(factory.Factory):
    FACTORY_FOR = Node

    ip_address = factory.LazyAttribute(lambda a: faker.internet.ip_address())
    uuid = factory.LazyAttribute(lambda a: random.randrange(1000, 1000000))
    port = factory.LazyAttribute(lambda a: random.randrange(1000, 10000))
    supernode = True

class TicketFactory(factory.Factory):
    source = factory.LazyAttribute(lambda a: NodeFactory())
    destination = factory.LazyAttribute(lambda a: NodeFactory())
    stream = factory.LazyAttribute(lambda a: StreamFactory())
