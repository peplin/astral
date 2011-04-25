import sys
import faker
import random

from astral.api.client import StreamsAPI, NodesAPI, TicketsAPI
from astral.models.tests.factories import NodeFactory
from astral.conf import settings

LOCAL_SERVER = "http://localhost:%s" % settings.PORT


class Cmdline():

    def get_cmdline(self, argv=None):
        if argv is None:
            argv = list(sys.argv)

        if len(argv) < 2:
            self.usage()
        else:
            if argv[1]=='-cn' or argv[1]== 'createfakenode':
                self.createNode(argv[1],argv[2])
            elif argv[1]=='-ln' or argv[1]== 'listnodes':
                self.listnodes(argv[1])
            elif argv[1]=='-ls' or argv[1]== 'liststreams':
                self.liststreams(argv[1])
            elif argv[1]=='-lt' or argv[1]== 'listtickets':
                self.listtickets(argv[1])
            elif argv[1]=='-st' or argv[1]== 'stream':
                self.stream(argv[1],argv[2],argv[3])
            elif argv[1]=='-w' or argv[1]== 'watch':
                self.watch(argv[1],argv[2])
            elif argv[1]=='-se' or argv[1]== 'seed':
                self.enableSeeding(argv[1],argv[2],argv[3])
            elif argv[1]=='-su' or argv[1]== 'streamurl':
                self.getStreamUrl(argv[1],argv[2])
            elif argv[1]=='-rt' or argv[1]== 'revoketicket':
                self.revokeTicket(argv[1],argv[2])
            elif argv[1]=='-dn' or argv[1]== 'deletenode':
                self.deletenode(argv[1],argv[2])
            elif argv[1]=='-sh' or argv[1]== 'shutdown':
                self.shutdown(argv[1])

    def usage(self):
        print """Usage: python astral/bin/astractl.py option

        Available options:
            createfakenode no.offakenodes or -cn no.offakenodes
            listnodes or -ln
            liststreams -ls
            listtickets or -lt
            stream streamname/id description or -st streamname/id description
            watch streamname/id or -w streamname/id
            seed streamname/id destuuid or -se streamname/id destuuid
            streamurl streamname/id or -su streamname/id
            revoketicket streamname/id or  -rt streamname/id
            deletenode nodeuuid or -dn nodeuuid
            shutdown or -sh
        """

    def createNode(self,arg,count):
        print "Selected option = ", arg
        for i in range(1,(int(count)+1)): 
            ip = faker.internet.ip_address()
            uuid = unicode(random.randrange(1000, 1000000))
            port = random.randrange(1000, 10000)
            print "&&&&&&&&&&&&&&&&", ip , uuid , port
            NodesAPI(LOCAL_SERVER).register({'ip_address': ip,'uuid': uuid,'port': port})

    def listnodes(self,arg):
        print "Selected option = ", arg
        print "List of nodes: ", NodesAPI(LOCAL_SERVER).list()

    def liststreams(self,arg):
        print "Selected option = ", arg
        print "List of streams: " , StreamsAPI(LOCAL_SERVER).list()

    def listtickets(self,arg):
        print "Selected option = ", arg
        print "List of tickets: " , TicketsAPI(LOCAL_SERVER).list()

    def stream(self,arg,name, description):
        print "Selected option = ", arg
        StreamsAPI(LOCAL_SERVER).create(name=name,
                    description=description)
        print "created stream, name = ", name, "description = ", description

    def watch(self,arg,streamId):
        print "Selected option = ", arg
        TicketsAPI(LOCAL_SERVER).create('/stream/'+streamId+'/tickets')
        print "streaming ",streamId

    def enableSeeding(self,arg,streamId,destuuid):
        print "Selected option = ", arg
        TicketsAPI(LOCAL_SERVER).create('/stream/'+streamId+'/tickets',destuuid)
        print "seeding ",streamId , "to", destuuid

    def getStreamUrl(self,arg,streamId):
        print "Selected option = ", arg

    def revokeTicket(self,arg,streamId):
        print "Selected option = ", arg
        url='stream/'+streamId+'/ticket'
        TicketsAPI(LOCAL_SERVER).cancel(url)

    def deletenode(self,arg,uuid):
        print "Selected option = ", arg
        url = "/node/" + uuid
        NodesAPI(LOCAL_SERVER).unregister(url)

    def shutdown(self,arg):
        print "Selected option = ", arg
        NodesAPI(LOCAL_SERVER).unregister()

def main():
    cmd = Cmdline()
    cmd.get_cmdline()


if __name__ == "__main__":
    main()
