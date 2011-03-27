from elixir import setup_all, create_all, metadata, Entity, session, drop_all
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from astral.models.node import Node
from astral.models.stream import Stream
from astral.models.ticket import Ticket


metadata.bind = create_engine("sqlite:///:memory:?check_same_thread=False",
        echo=True, poolclass=StaticPool)

setup_all()
create_all()