import factory
import faker

from astral.models.stream import Stream

ELIXIR_CREATION = lambda class_to_create, **kwargs: class_to_create(**kwargs)
factory.Factory.set_creation_function(ELIXIR_CREATION)

class StreamFactory(factory.Factory):
    name = factory.LazyAttribute(lambda a: ' '.join(faker.lorem.words()))
