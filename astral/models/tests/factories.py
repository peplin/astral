import factory
import faker
import random

from astral.models.stream import Stream
from astral.models.node import Node


ELIXIR_CREATION = lambda class_to_create, **kwargs: class_to_create(**kwargs)
factory.Factory.set_creation_function(ELIXIR_CREATION)


class StreamFactory(factory.Factory):
    name = factory.LazyAttribute(lambda a: ' '.join(faker.lorem.words()))


class NodeFactory(factory.Factory):
    ip_address = factory.LazyAttribute(lambda a: faker.internet.ip_address())
    uuid = factory.LazyAttribute(lambda a: random.randrange(1000, 1000000))
    port = factory.LazyAttribute(lambda a: random.randrange(1000, 10000))
