import sys

class Cmdline:

    def get_cmdline(self, argv=None):
        if argv is None:
            argv = list(sys.argv)

        if len(argv) < 2:
            self.usage()
            return

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



    def usage(self):
        print ("Usage: python cmdline_controller "
                "stream/watch/shutdown/liststreams/listtickets/listnodes/ "
                "or -st/-w/-sh/-ls/-lt/-ln")

    def stream(self,arg):
        print "Selected option = ", arg
        # create JSON message and send to server

    def listtickets(self,arg):
        print "Selected option = ", arg
        # create JSON message and send to server

    def listnodes(self,arg):
        print "Selected option = ", arg
        # create JSON message and send to server

    def liststreams(self,arg):
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
