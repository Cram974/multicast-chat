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
		self.shouldrun = True
		
	def run(self):
		while self.shouldrun: 
			try:
				# TO DO Recv message
			except socket.timeout:
				continue
		# TO DO Close recv socket
	
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
		# BEGIN ------ TO DO 
		# Create recv socket
		# SO_REUSEADDR and SO_REUSEPORT to allow multiple instances of this program to run on a host
		#  BIND on Multicast address
		# multicast request to fill
		# join the group
		# END ------ TO DO 

		self.recvsock.settimeout(1)	

		self.prompt=self.name + "@" + self.room + "# "		
		print "*** Room is joined. ***"
		# to recv
		#  TO DO Create a thread to listen on the recv socket 
		# to send
		# TO Create socket to send message	
				
	except:
		traceback.print_exc()
		usage("Socket connection error: aborting ...")	


    def run(self):
	blankcount = 0 
	sys.stdout.write(self.prompt)
	while blankcount < Configuration.MAX_BLANKS_THEN_QUIT :
		line = sys.stdin.readline().rstrip()
		if  line:
			# Somethnig to send: "name > line"
			# TO DO
			blankcount = 0
		else:
			blankcount = blankcount + 1
	self.listensocket.stoplistening()
						

#*************************************************************************
#=======================================
##                 MAIN               ##
#=======================================
	
if __name__ == '__main__':
	name=sys.argv[0]
	group = Room(getopts(sys.argv[1:]))
 	group.run()
        sys.exit(0)
