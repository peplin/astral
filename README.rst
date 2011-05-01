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

* tornado >= 1.2.1
* sqlalchemy >= 0.6.6
* Elixir >= 0.7.1
* restkit >= 3.2.0


Development Requirements
-------------------------

.. _nosetests: http://somethingaboutorange.com/mrl/projects/nose/0.11.2/
.. _mockito-python: http://code.google.com/p/mockito-python/

The astral test suite requires:

* nosetests_ >= 0.11.4
* mockito-python_ >= 0.5.10
* python-faker >= 0.2.3
* factory-boy >= 1.0.0

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
application is running at http://astral-video.heroku.com, and the Python package
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

* A central web application (astral-web_) exposes both HTML views for users as
    well as a JSON API for nodes to bootstrap themselves
* Nodes bootstrap from static configuration files as well as from the central
    webapp
* Nodes register with a primary supernode
* Nodes promote themselves to supernode if none are available with sufficient
    capacity
* Nodes failover to other supernodes if their choosen primary leaves the
    network, or optionally promote themselves if no others are available
* Nodes request “tickets” for a stream, which is a promise from another node
    that it will forward the stream, using selective multicast (i.e. to
    supernodes only)
* Users running a node can view a list of available streams in a web browser
* Incoming forwarded streams failover to other providers if the sender leaves
    the network
* Flash-based stream consumer in the web browser handles temporary breaks in the
    stream seamlessly
* Nodes perform a proper shutdown by informing other nodes and stream receivers
    of their change in status
* Stream tickets time out after a series of failed heartbeat messages, in order
    to accommodate improper node shutdown (i.e. unexpected failure)
* Local node is controlled via Javascript with HTTP requests in the browser
* Local node can also be controlled with HTTP requests from the command line

Design & Architecture
==============

Astral is based on a single, flexible peer-to-peer client application with a few
different user interfaces. The application itself is written in Python, and runs
as a background process that is invisible to the casual user. The nodes use HTTP
and individual embedded web servers to communicate, and the Adobe Flash-based
Real-Time Messaging Protocol to access video devices, encode a video stream, and
send it with other clients. Each node streaming from a video device runs an RTMP
server which connects to a video provider Flash applet in the local browser.

After installing the Astral client, the user is directed to a web application
(via a web browser) that displays a list of all available streams. Each stream
has a preview and metadata about the content, provided by the producer and the
source node. When a user selects a stream to watch, an Astral browser extension
communicates their choice to the background process via Javascript with HTTP
requests.

Once the stream is forwarded to the client by at least one other node on the
network, the user can view it directly in the browser or in any other streaming
media player (by clicking a stream link embedded in the web page).

The Astral client is designed with flexibility in mind. A node can be any of a
content producer, consumer or seeder. These three types of nodes make up the
clients of the overlay network, pictured in Figure 2. There are three basic
actions for consumer nodes, described here in figures 3, 4 and 5. A node
announces its presence in the network (and thus its candidacy for stream
forwarding) by sending an HTTP POST request to its choosen supernode with itself
as the data. When a user requests to watch a stream, the node propagates its
interest in this stream through to its neighbor nodes until a node is found that
is capable and willing to forward the content. When a node leaves the network,
it performs a few critical shutdown steps to give other nodes ample opportunity
to adjust their stream source or target; it sends HTTP DELETE requests to any
nodes to which it is forwarding a stream, any child nodes, and (if it has one)
its primary supernode. This keeps data as consistent as possible in the network
without the overhead of excessive heartbeat messages.Go

Node Communication
-------------------

The original design of Astral included intra-node messaging via the ZeroMQ
messaging framework. ZeroMQ is message-oriented library that sits on top of TCP
sockets to provide very fast messaging between threads, applications and
networked machines. Astral requires occasional messaging between peers, and
ZeroMQ would be a good fit. In the process of implementing the messaging
handling code, however, we realized that much of the logic for routing messages
is already implemented in widely available web frameworks. Web services that use
the Representational State Transfer (ReST) style are also a natural fit for the
type of messages that Astral nodes exchange - e.g. creating and deleting nodes,
streams and stream forward requests. 

With this insight, we replaced the messaging core with an embedded web server
(specifically the Tornado web framework from Facebook). Each node starts an
instance of this server listening on port 8000 at startup, and exposes a simple
ReSTful API that accepts and returns data in the JSON format. An additional
advantage of this approach is that it enabled Astral to use simple HTTP requests
in Javascript to communicate with the node from a web browser.

Source Stream Uploading
-----------------

Astral currently implements source streaming from the browser only. The original
design allowed producers to direct any existing streaming device or client at a
local TCP socket, but a switch to using the Adobe Flash-based protocol RTMP made
this more challenging. Our target external device, VLC, does not currently
support sending a video stream to an RTMP server. As planned, the streaming
interface is extremely simple; it is very similar to hitting play on a YouTube.
The Flash applet also natively supports streaming from any attached device, be
it a USB webcam or Firewire HD camera.

User Interface for Selecting Stream
-----------------

The user interface for Astral proceeded exactly as planned. It is deployed to a
central web server, and accessed via a traditional web browser by all clients.
After selecting a stream, the user can view the video embedded in the page via a
Flash consumer applet. The page also displays the RTMP server’s URL, so users
can connect with another streaming client if they so choose.

Stream Seeding
----------------

Nodes in the overlay network can volunteer to seed a specific stream in order to
increase its availability. This requires no special logic - the only difference
between a seeding node and a regular consumer is that the seeder does not
connect to the stream with a Flash consumer.

Peer-to-Peer Overlay Network Communication
------------------

Astral clients bootstrap themselves with knowledge of the overlay network obtain
via static configuration files, the origin webserver, and finally, their primary
supernode. When a node joins the network, it requests a partial list of
supernodes from the origin web application. It selects the closest supernode
from this list (based on ping round-trip time) and attempts to register with it.
If the supernode is already at capacity (currently a hard-coded limit of 100
children), the node continues down the sorted list of supernodes until one
accepts it. If no supernodes are available or none have capacity, a node
promotes itself to supernode status, extending the capacity of the network
automatically.
