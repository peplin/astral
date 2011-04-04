import sys
from astral.api.client import Streams
from astral.api.client import Nodes
from astral.api.client import Tickets
import json
from astral.api.client import NodeAPI
from astral.conf import settings

class Cmdline():
       
    def get_cmdline(self, argv=None):
        if argv is None:
            argv = list(sys.argv)
        
        if len(argv) < 2:
            self.usage()
        
	else:
                       
	    if argv[1]=='-st' or argv[1]== 'stream':
                self.stream(argv[1])

            elif argv[1]=='-w' or argv[1]== 'watch':
                self.watch(argv[1])

            elif argv[1]=='-sh' or argv[1]== 'shutdown':
                self.shutdown(argv[1])

            elif argv[1]=='-ls' or argv[1]== 'liststreams':
                self.liststreams(argv[1])

            elif argv[1]=='-lt' or argv[1]== 'listtickets':
                self.listtickets(argv[1])

            elif argv[1]=='-ln' or argv[1]== 'listnodes':
                self.listnodes(argv[1])

            elif argv[1]=='-s' or argv[1]== 'start':
                self.start(argv[1])

           
        
    def usage(self):
        print "Usage: python   cmdline_controller.py    start/stream/watch uri /shutdown/liststreams/listtickets/listnodes/ or -s/-st/-w uri /-sh/-ls/-lt/-ln"

    def liststreams(self,arg):
        print "Selected option = ", arg
        # create JSON message and send to server
	#obj_temp = json.JSONEncoder().encode({ "url": "/stream" })
        print "List of streams: " , Streams(settings.ASTRAL_WEBSERVER).list()

    def listtickets(self,arg):
        print "Selected option = ", arg
        # create JSON message and send to server
        print "List of tickets: " , Tickets(settings.ASTRAL_WEBSERVER).list()

    def listnodes(self,arg):
        print "Selected option = ", arg
        # create JSON message and send to server
        print "List of nodes: ", Nodes(settings.ASTRAL_WEBSERVER).list()

    def start(self,arg):
        print "Selected option = ", arg
        # create JSON message and send to server

    def stream(self,arg):
        print "Selected option = ", arg
        # create JSON message and send to server

    def watch(self,arg):
        print "Selected option = ", arg       
        # create JSON message and send to server

    def shutdown(self,arg):
        print "Selected option = ", arg      
        # create JSON message and send to server

def main():
    cmd = Cmdline()
    cmd.get_cmdline()
    

if __name__ == "__main__":
    main()
