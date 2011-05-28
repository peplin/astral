astral
==============

.. _astral: http://github.com/peplin/astral
.. _Python: http://python.org/

astral_ is a peer-to-peer content distribution network specifically built for
live, streaming media. Without IP multicast, if content producers want to stream
live events to consumers, they are forced to create separate feeds for each
user. A peer-to-peer approach is more efficient and offloads much of the work
from the origin servers to the edges of the network.

This project was completed over the course of the Spring 2011 semester in the
Distributed Systems (18-842) course at Carnegie Mellon University, taught by
Professor Bill Nace.


Requirements
------------

Astral requires Python_ 2.6 or greater. The Python package dependencies are:

- tornado >= 1.2.1
- sqlalchemy >= 0.6.6
- Elixir >= 0.7.1
- restkit >= 3.2.0


Development Requirements
-------------------------

.. _nosetests: http://somethingaboutorange.com/mrl/projects/nose/0.11.2/
.. _mockito-python: http://code.google.com/p/mockito-python/

The astral test suite requires:

- nosetests_ >= 0.11.4
- mockito-python_ >= 0.5.10
- python-faker >= 0.2.3
- factory-boy >= 1.0.0

Installation
------------

Astral is currently available only as a source distribution, so to install you
must clone the source from GitHub and install::

    $ git clone git://github.com/peplin/astral.git
    $ cd astral
    $ pip install .

Usage
------

.. _astral-web: http://github.com/peplin/astral-web

Astral is a two part system, made up of a network of Astral nodes and a single,
centralized web application (astral-web_). At the moment, an instance of the web
application is running at http://astral.rhubarbtech.com, and the Python package
is configured to connect to this address by default.

This repository contains the application to run an individual node, one that is
sending, consuming or seeding a video stream in the network.

Use the ``astralnode`` executable to start the node::

    $ astralnode -h
    Usage: astralnode [options]

    Options:
      -s SETTINGS_MODULE, --settings=SETTINGS_MODULE
                            Name of the module to read settings from.
      -D DAEMONIZE, --daemonize=DAEMONIZE
                            Daemonize the application
      -u UUID_OVERRIDE, --uuid=UUID_OVERRIDE
                            UUID override, for testing multiple nodes on one box
      -l UPSTREAM_LIMIT, --upstream-limit=UPSTREAM_LIMIT
                            Maximum upload bandwidth to use for forwarding streams
      --version             show program's version number and exit
      -h, --help            show this help message and exit

Running ``astralnode`` with no options will set it to listen on port 8000, and
does not fork to the background.

Summary of Features
===================

.. _article: http://christopherpeplin.com/2011/05/astral/

- A central web application (astral-web_) exposes both HTML views for users as
  well as a JSON API for nodes to bootstrap themselves
- Nodes bootstrap from static configuration files as well as from the central
  webapp
- Nodes register with a primary supernode
- Nodes promote themselves to supernode if none are available with sufficient
  capacity
- Nodes failover to other supernodes if their choosen primary leaves the
  network, or optionally promote themselves if no others are available
- Nodes request “tickets” for a stream, which is a promise from another node
  that it will forward the stream, using selective multicast (i.e. to
  supernodes only)
- Users running a node can view a list of available streams in a web browser
- Incoming forwarded streams failover to other providers if the sender leaves
  the network
- Flash-based stream consumer in the web browser handles temporary breaks in the
  stream seamlessly
- Nodes perform a proper shutdown by informing other nodes and stream receivers
  of their change in status
- Stream tickets time out after a series of failed heartbeat messages, in order
  to accommodate improper node shutdown (i.e. unexpected failure)
- Local node is controlled via Javascript with HTTP requests in the browser
- Local node can also be controlled with HTTP requests from the command line

For a more in-depth writeup, see this article_.
