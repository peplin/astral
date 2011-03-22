from elixir import setup_all, create_all, metadata

from astral.models.node import Node
from astral.models.stream import Stream
from astral.models.ticket import Ticket


metadata.bind = "sqlite:///:memory:"
metadata.bind.echo = True

setup_all()
create_all()
