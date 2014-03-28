#!/usr/bin/python
# Copyright (c) 2014 University of La Reunion - LIM - France
# Author:   YOUR NAME
#-------------------------------------------------------------------------
# Goals :			    				      	      
# ------          							     
#     Multicast node
#*************************************************************************

#====================== Import section
import sys, signal,string
from socket import socket, AF_INET, SOCK_DGRAM, timeout, SOL_SOCKET, SO_SNDBUF
from optparse import OptionParser

#====================================================
# Constantes
#====================================================
MESSAGELG=1000
MCAST_PORT=10000
MAX_DELAY=120  # in sec
class MSGTYPE:
	root="ROOT"
	toor="TOOR"
        rreg="RREG"
	nreg="NREG"
        yreg="YREG"
MASTER='194.199.68.163'
#====================================================
# Variables
#====================================================
parent=()

#====================================================
# Procedures Definition
#====================================================
def usage(msg):
        sys.stdin.write("Usage: %s servaddr [file]\n %s \n" % (sys.argv[0], msg))
        sys.exit(1)

def send_msg(dest, type, data):
	global sock

	msg=type[:4]+"\r\n"+ data
	print "msg: ", msg
	sock.sendto(msg,dest)



#*************************************************************************
#=======================================
##                 MAIN               ##
#=======================================
# Process command line

parser = OptionParser(usage= 'usage: %prog [options]')
parser.set_defaults(server='127.0.0.1')
parser.add_option("-s", action='store', type='string', dest="server", help='Server IP address')

(options, args) = parser.parse_args()


sock = socket(AF_INET, SOCK_DGRAM)
rpaddr = (options.server, MCAST_PORT)
sock.settimeout(3.0)


# register a  root
send_msg(rpaddr, MSGTYPE.rreg, '')
data, addr =sock.recvfrom(1024)
print "from: ", addr,  " data : ", data

myaddr=sock.getsockname()
print "my addr: ", myaddr

 
#find a root
send_msg(rpaddr, MSGTYPE.root, '')
data, addr =sock.recvfrom(1024)
print "from: ", addr,  " data : ", data

type=data[:4]
rootaddr=tuple(string.split(string.lstrip(data[4:])))
print rootaddr



sock.close()
sys.exit(0)




#print stat
sys.exit(0)

#--------------------------------------------------------------------------
#Peer_loop()
#   While (1)
#     wait(event)
#     switch(event)
#       timeout:
#          do_treework()
#          schedule_timer()
#      received:
#          handle_msg()
