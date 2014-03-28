#!/usr/bin/python
# Copyright (c) 2014 University of La Reunion - LIM - France
# Author:   Marc Dijoux
#-------------------------------------------------------------------------
# Goals :			    				      	      
# ------          							     
#     Multicast node
#*************************************************************************

#======================
# Import section
#======================
import sys, signal, string, random
from threading import *
from socket import *
from optparse import OptionParser
        
def setTimeout(func, time):
    t = Timer(time, func)
    t.start()
    return t

class TimedOutObj:
    def __init__(self, obj, collection, time):
        self.obj = obj
        self.collection = collection
        self.time = time
        
    def register(self):
        self.collection.append(self)
        self.resetTimeout()
        
    def unregister(self):
        self.unsetTimeout()
        self.collection.remove(self)
            
    def unsetTimeout(self):
        if self.timeout:
            self.timeout.cancel()
            self.timeout = None
            
    def resetTimeout(self):
        self.unsetTimeout()
        self.timeout = setTimeout(self.unregister, self.time)

        
#====================================================
# Constantes
#====================================================
MCAST_PORT=10000
DATA_PORT=10001

MCAST_MSG_LEN=1024

ROOT_REFRESH=120 #seconds
NODE_REFRESH=120 #seconds
CHILDREN_MAX=3
CHILDREN_TIMEOUT=180 #seconds
SOCKET_TIMEOUT=3.0

#Message types
ROOT="ROOT"
TOOR="TOOR"
RREG="RREG"
YREG="YREG"
NREG="NREG"
RJOI="RJOI"
YJOI="YJOI"
NJOI="NJOI"

class MC_Node(Thread):
    
    #====================================================
    # Constructor
    #====================================================
    def __init__(self, rp_addr):
        Thread.__init__( self )
        self.mcast_sock = socket(AF_INET, SOCK_DGRAM)
        self.mcast_sock.bind(('', MCAST_PORT))
        
        self.rp_addr = rp_addr
        
        #Resolve adresses
        self.addr = self.mcast_sock.getsockname()
        
        self.data_addr = (self.addr[0], DATA_PORT) 
        self.childrens = []
        
    def mcast_send(self, dest, type, data):
        msg=type[:4]+"\r\n"+data
        print 'to: ', dest
        print 'type:', type, ' data: ', data
        self.mcast_sock.sendto(msg,dest)
        
    def mcast_recv(self):   
        data, addr = self.mcast_sock.recvfrom(MCAST_MSG_LEN) 
        print 'from: ', addr
        print 'type: ', data[:4], ' data: ', data[6:]
        return data
    
    # Root stuff
    def getRoot(self):
        self.mcast_send(self.rp_addr, ROOT, '')
        data = self.mcast_recv()

        if data[:4] == TOOR:
            root = tuple(string.split(string.lstrip(data[4:])))
            if len(root) == 2:
                root = (root[0], int(root[1]))
            return root
    
        #TODO throw an error
        return ()
        
    
    def registerRoot(self):
        self.mcast_send(self.rp_addr, RREG, '')
        data = self.mcast_recv()
        if  data[:4]== YREG:
            return True
        elif data[:4] == NREG:
            return False
        
        #TODO throw an error
        return

    
    def updateRoot(self):
        if self.registerRoot():
            self.runRoot()
            return

    def runRoot(self):
        self.root_timeout = setTimeout(self.updateRoot, ROOT_REFRESH)
    
    # Node stuff
    def registerNode(self, node_addr):
        self.mcast_send(node_addr, RJOI, '')
        data = self.mcast_recv()

        if data[:4] == YJOI:
                # Success -> set parent
                self.parent = node_addr
                self.runNode()
        elif data[:4] == NJOI:
                # Failure -> register on random children
                child_addr = tuple(data[4:].split('\r\n')[random.randint(0, 2)].split())
                nodeRegister(child_addr)
    def updateNode(self):
        self.mcast_send(self.parent, RJOI, '')
        self.mcast_sock.settimeout(SOCKET_TIMEOUT)
        for i in range(0, 3):
            try:
                data = self.mcast_recv()
                if data[:4] == YJOI:
                    self.mcast_sock.settimeout(None)
                    self.runNode()
                return
            except:
                pass
        self.mcast_sock.settimeout(None)
        self.nodeRegister(self.getRoot())
    def runNode(self):
        self.node_timeout = setTimeout(self.updateNode, NODE_REFRESH)
        
    # Child stuff
    def registerChild(child_addr):
        if len(self.childrens) < CHILDREN_MAX:
            self.childrens.append(child_addr)
            child = TimedOutObj(child_addr, self.childrens, CHILDREN_TIMEOUT)
            child.register
            self.mcast_send(child_addr, YJOI, '')
        else:
            self.mcast_send(child_addr, NJOI, "\r\n".join(" ".join(x) for x in childrens))
    def dataLoop(self):
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.bind(('', DATA_PORT))
        while True:
            try:
                data, addr = sock.recvfrom(1024)
                print "DATA: ", data
                for child in self.childrens:
                    sock.sendto(data, (child.obj[0], DATA_PORT))
            except KeyboardInterrupt:
                print
        #close
        self.data_sock.close()
        
    def run(self):
        root = self.getRoot()
        if root == ():
            if self.registerRoot():
                #This node is the root one
                #Must keep alive
                self.runRoot()
                
            else:
                root = self.getRoot()
        if root != ():
            self.registerNode(root)
        
        Thread(target=self.dataLoop).start()
        while True:
            try:
                data, addr = self.mcast_sock.recvfrom(1024)
                type = data[:4]
                if type==RJOI:
                    child = next((x for x in self.childrens if x.obj == addr), None)
                    if child is None:
                        childRegister(addr)
                    else:
                        child.resetTimeout()
                        self.mcast_send(child.obj, YJOI, '')
            except KeyboardInterrupt:
                print
        #close
        self.mcast_sock.close()
            
parser = OptionParser(usage= 'usage: %prog [options]')
parser.set_defaults(server="127.0.0.1")
parser.add_option("-s", action='store', type='string', dest="server", help='Server IP address')

(options, args) = parser.parse_args()

server = MC_Node((options.server, MCAST_PORT))
server.start()