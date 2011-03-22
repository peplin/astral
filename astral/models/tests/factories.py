import factory
import faker
import random

from astral.models.stream import Stream
from astral.models.node import Node
from astral.models.ticket import Ticket


ELIXIR_CREATION = lambda class_to_create, **kwargs: class_to_create(**kwargs)
factory.Factory.set_creation_function(ELIXIR_CREATION)


class StreamFactory(factory.Factory):
    id = factory.Sequence(lambda n: int(n) + 1)
    name = factory.LazyAttribute(lambda a: ' '.join(faker.lorem.words()))


class NodeFactory(factory.Factory):
    ip_address = factory.LazyAttribute(lambda a: faker.internet.ip_address())
    uuid = factory.LazyAttribute(lambda a: random.randrange(1000, 1000000))
    port = factory.LazyAttribute(lambda a: random.randrange(1000, 10000))


class TicketFactory(factory.Factory):
    node = factory.LazyAttribute(lambda a: NodeFactory())
    stream = factory.LazyAttribute(lambda a: StreamFactory())
