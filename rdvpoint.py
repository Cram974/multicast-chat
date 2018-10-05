#!/usr/bin/python
# -------------------------------------------------------------------------
# Goals :
# ------
#     To record the root of the multicast tree
# -------------------------------------------------------------------------

# *************************************************************************

# ====================== Import section
import sys
import string
from socket import socket, AF_INET, SOCK_DGRAM
import signal
import time
import traceback

# ====================================================
# Constantes
# ====================================================
MCAST_PORT = 10000
MAX_DELAY = 180  # in sec


class MSGTYPE:
    root = "ROOT"
    toor = "TOOR"
    rreg = "RREG"
    nreg = "NREG"
    yreg = "YREG"
    erro = "ERRO"


# ====================================================
# Variables
# ====================================================
rootaddr = ()

DEBUG = 0
# ====================================================
# Procedures Definition
# ====================================================


def usage(name):
    print >>sys.stderr,  "Usage: python %s server|client [options] [arguments]" % name
    exit(1)


class Timeout():
    """Timeout class using ALARM signal."""
    class fire(Exception):
        pass

    def __init__(self):
        signal.signal(signal.SIGALRM, self.raise_timeout)

    def schedule(self, sec):
        signal.alarm(sec)

    def cancel(self):
        signal.alarm(0)    # disable alarm

    def raise_timeout(self, *args):
        raise Timeout.fire()


class Message():
    """Message class to send and receive HMTP message"""

    def __init__(self, sock):
        self.sock = sock
        self.msg = ''

    def recv(self):
        self.msg, self.addr = self.sock.recvfrom(1024)
        print("<-- ", self.addr, "**%s**" % self.msg)
        self.type = self.msg[:4]
        if DEBUG:
            print("recv msg: ", self.type)
        return self.type

    def send(self, dest, type, data):
        if dest == '':
            dest = self.addr
        self.msg = type[:4]+"\r\n" + data
        print("--> ", dest, "**%s**" % self.msg)
        self.sock.sendto(self.msg, dest)

    def send_error(self, msge):
        msg = MSGTYPE.erro + "\r\n" + msge + "\r\n" + self.msg
        print("--> **%s**" % msg)
        self.sock.sendto(msg, self.addr)

    def get_data(self):
        return string.lstrip(self.msg[4:])

    def get_addr(self):
        return self.addr


def print_stat():
    print("-"*40)
    print("number of request:", nbreq)
    print("number of registration:", nbreg)
    print("number of new root:", nbroot)
    print("-"*40)

# *************************************************************************
# =======================================
##                 MAIN               ##
# =======================================

# Process command line


# ------ counters for stats
nbroot = 0
nbreg = 0
nbreq = 0

# Create Signaling socket
sock = socket(AF_INET, SOCK_DGRAM)
sock.bind(('', MCAST_PORT))

# Create the socket wrapper
msg = Message(sock)

# Create the Soft State timeout
ssto = Timeout()


# Main Loop
while True:
    try:
        print("-------------------------Waiting.....")
        type = msg.recv()
        if type == MSGTYPE.root:
            if rootaddr:
                payload = "%s %d" % (rootaddr[0], rootaddr[1])
            else:
                payload = ""
            msg.send('', MSGTYPE.toor, payload)
            nbreq += 1
        elif type == MSGTYPE.rreg:
            nbreg += 1
            recvaddr = msg.get_addr()
            if rootaddr:
                if recvaddr == rootaddr:
                    ssto.schedule(MAX_DELAY)
                    msg.send('', MSGTYPE.yreg, '')
                else:
                    msg.send('', MSGTYPE.nreg, '')
            else:
                rootaddr = recvaddr
                ssto.schedule(MAX_DELAY)
                msg.send('', MSGTYPE.yreg, '')
                nbroot += 1
        else:
            msg.send_error('Error Unknown message')
    except ssto.fire:
        # erase soft state on root addr
        print("*****    Remove root node")
        rootaddr = ()

    except KeyboardInterrupt:
        print_stat()
        raise
    except:
        traceback.print_exc()
sock.close()
sys.exit(0)
