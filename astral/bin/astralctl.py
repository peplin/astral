import sys
from astral.api.client import StreamsAPI
from astral.api.client import NodesAPI
from astral.api.client import TicketsAPI
import json
from astral.api.client import NodeAPI
from astral.conf import settings
from astral.node.base import LocalNode
from astral.bin.astralnode import NodeCommand
from astral.api.handlers.node import NodeHandler
from astral.models.node import Node

LOCAL_SERVER = "http://localhost:8000"

class Cmdline():
       
    def get_cmdline(self, argv=None):
        if argv is None:
            argv = list(sys.argv)
        
        if len(argv) < 2:
            self.usage()
        
	else:
                       
	    if argv[1]=='-st' or argv[1]== 'stream':
                self.stream(argv[1],argv[2],argv[3])

            elif argv[1]=='-w' or argv[1]== 'watch':
                self.watch(argv[1],argv[2])

            elif argv[1]=='-sh' or argv[1]== 'shutdown':
                self.shutdown(argv[1])

            elif argv[1]=='-ls' or argv[1]== 'liststreams':
                self.liststreams(argv[1])

            elif argv[1]=='-lt' or argv[1]== 'listtickets':
                self.listtickets(argv[1])

            elif argv[1]=='-ln' or argv[1]== 'listnodes':
                self.listnodes(argv[1])

            elif argv[1]=='-rt' or argv[1]== 'revoketicket':
                self.revokeTicket(argv[1],argv[2])

            elif argv[1]=='-su' or argv[1]== 'streamurl':
                self.getStreamUrl(argv[1])

            elif argv[1]=='-se' or argv[1]== 'seed':
                self.enableSeeding(argv[1])

            elif argv[1]=='-cn' or argv[1]== 'createnode':
                self.createNode(argv[1])

            elif argv[1]=='-s' or argv[1]== 'start':
                self.start(argv[1])

           
        
    def usage(self):
        print "Usage: python   cmdline_controller.py    start/stream/watch uri /shutdown/liststreams/listtickets/listnodes/revoketicket ticketIdentification/streamurl xxx/seed/createnode or -s/- st/-w uri /-sh/-ls/-lt/-ln/-rt identification/-su xxx/-se/-cn"

    def liststreams(self,arg):
        print "Selected option = ", arg
        # create JSON message and send to server
	#obj_temp = json.JSONEncoder().encode({ "url": "/stream" })
        print "List of streams: " , StreamsAPI(LOCAL_SERVER).list()

    def listtickets(self,arg):
        print "Selected option = ", arg
        # create JSON message and send to server
        print "List of tickets: " , TicketsAPI(LOCAL_SERVER).list()

    def listnodes(self,arg):
        print "Selected option = ", arg
        # create JSON message and send to server
        print "List of nodes: ", NodesAPI(LOCAL_SERVER).list()

    def start(self,arg):
        print "Selected option = ", arg
        # create JSON message and send to server
        start = NodeCommand()
        start.run()

    def stream(self,arg,name, description):
        print "Selected option = ", arg
        # create JSON message and send to server
        StreamsAPI(LOCAL_SERVER).create(name=name,
                    description=description)
        print "created stream, name = ", name, "description = ", description

    def watch(self,arg,uri):
        print "Selected option = ", arg       
        # create JSON message and send to server

    def getStreamUrl(self,arg):
        print "Selected option = ", arg       
        # create JSON message and send to server

    def enableSeeding(self,arg):
        print "Selected option = ", arg       
        # create JSON message and send to server

   def createNode(self,arg):
        print "Selected option = ", arg       
        # create JSON message and send to server

    def revokeTicket(self,arg,url):
        print "Selected option = ", arg       
        # create JSON message and send to server
        TicketsAPI(LOCAL_SERVER).cancel(url)

    def shutdown(self,arg):
        print "Selected option = ", arg      
        # create JSON message and send to server
	shut = NodesAPI(LOCAL_SERVER)
        #url = Node()
        shut.unregister()
  #      raise KeyboardInterrupt

def main():
    cmd = Cmdline()
    cmd.get_cmdline()
    

if __name__ == "__main__":
    main()
