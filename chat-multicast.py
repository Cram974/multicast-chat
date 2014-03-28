#!/usr/bin/python
# Multicasting chat

#*************************************************************************
#====================== Import section
import sys, socket, struct, traceback
from threading import Thread

#====================================================
# Constantes
#====================================================
class Configuration:
    MAX_BLANKS_THEN_QUIT = 3
    UNKNOWN = "(Unknown)"
    MCAST_PORT = 5000

#====================================================
# Procedures Definition
#====================================================	

def usage(msg):
    print >>sys.stderr, msg
    print >>sys.stderr,  "Usage: python %s [options] " % name
    print >>sys.stderr,  "Options : "
    print >>sys.stderr,  "         -name <nickname>"
    print >>sys.stderr,  "         -room <@ IP>"
    exit(1)


def getopts(args):
    opt = {}
    if len(args) % 2 != 0:
        usage(("Wrong number of args %d"%len(args)))
    key = None; val = None

    for arg in args:
        if arg[0] == "-":
            if key != None:
                usage("Initialization problem on key name")
            key = arg[1:]
            if key == "":
                usage("key name is empty")
        else:
            if key == None:
                usage(("value without key name: %s"% arg))
            opt[key] = arg
            key = None
    return opt

class ListenSocket(Thread):
    def __init__ (self, sock):
        Thread.__init__(self)
        self.sock = sock
        self.prompt = prompt
        self.shouldrun = True

    def run(self):
        while self.shouldrun: 
            try:
                #Recv message
                print self.sock.recvfrom(1024)[0]
            except socket.timeout:
                continue
        #Close recv socket
        self.sock.close()

    def stoplistening(self):
        self.shouldrun = False

class Room:
    def __init__(self, opt):
        self.name = Configuration.UNKNOWN
        self.room = Configuration.UNKNOWN
        if opt.has_key("name"):
            self.name = opt["name"]
        else:
            usage("Please define your nickname")
        if opt.has_key("room"):
            self.room = opt["room"]
        else:
            usage("Please provide your chat room")
        # try to join the grooup
        try:
            # Create recv socket
            self.recvsock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            # SO_REUSEADDR and SO_REUSEPORT to allow multiple instances of this program to run on a host
            self.recvsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.recvsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            #  BIND on Multicast address
            self.recvsock.bind((self.room, 5000))
            # multicast request to fill
            mreq = struct.pack("=4sl", socket.inet_aton(self.room), socket.INADDR_ANY) 
            # join the group
            self.recvsock.setsockopt( socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

            self.recvsock.settimeout(1)	

            self.prompt=self.name + "@" + self.room + "# "		
            print "*** Room is joined. ***"
            # to recv
            # Create a thread to listen on the recv socket 
            self.listensocket = ListenSocket(self.recvsock)
            self.listensocket.start()
            # to send
            # Create socket to send message	
            self.sendsock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            self.send(self.name + " joined the room")

        except:
            traceback.print_exc()
            usage("Socket connection error: aborting ...")	

    def send(self, msg):
        self.sendsock.sendto(msg, (self.room, 5000))

    def run(self):
        blankcount = 0 
        sys.stdout.write(self.prompt)
        while blankcount < Configuration.MAX_BLANKS_THEN_QUIT :
            line = sys.stdin.readline().rstrip()
            if  line:
                # Somethnig to send: "name > line"
                self.send(self.name +" say: "+line)
                blankcount = 0
            else:
                blankcount = blankcount + 1
        self.listensocket.stoplistening()
        self.sendsock.close()


#*************************************************************************
#=======================================
##                 MAIN               ##
#=======================================

if __name__ == '__main__':
    name=sys.argv[0]
    group = Room(getopts(sys.argv[1:]))
    group.run()
    sys.exit(0)
