# -*- test-case-name: mold.test.test_process -*-
"""
XXX
"""

from twisted.internet import protocol, defer, interfaces
from twisted.protocols.basic import NetstringReceiver
from twisted.python.runtime import platform

from zope.interface import implements

import os

from mold import ch3



class Channel3Protocol(protocol.ProcessProtocol):
    """
    XXX
    
    @ivar done: A C{Deferred} which will fire when the process has 
        finished.
    @ivar started: A C{Deferred} which fires on my L{connectionMade}.
    """
    
    implements(interfaces.IProcessTransport)
    
    
    def __init__(self, name, channel3_receiver):
        self.done = defer.Deferred()
        self.started = defer.Deferred()
        self.name = name
        self._ch3_receiver = channel3_receiver
        
        # some initialization happens in makeConnection
        self._ch3_netstring = NetstringReceiver()
        self._ch3_netstring.makeConnection(None)
        self._ch3_netstring.stringReceived = self._ch3DataReceived


    def connectionMade(self):
        self.started.callback(self)


    def childDataReceived(self, childfd, data):
        if childfd == 3:
            self._ch3_netstring.dataReceived(data)
        else:
            self._ch3_receiver(ch3.fd(self.name, childfd, data))


    def _ch3DataReceived(self, data):
        name, key, val = ch3.decode(data)
        name = '.'.join([self.name, name])
        self._ch3_receiver(ch3.Message(name, key, val))


    def processEnded(self, status):
        """
        XXX
        """
        self._ch3_receiver(ch3.exit(self.name,
                                    status.value.exitCode,
                                    status.value.signal))
        self.done.callback(status)


    # IProcessTransport
    
    @property
    def pid(self):
        if self.transport:
            return self.transport.pid


    def closeStdin(self):
        return self.transport.closeStdin()


    def closeStdout(self):
        return self.transport.closeStdout()


    def closeStderr(self):
        return self.transport.closeStderr()


    def closeChildFD(self, descriptor):
        return self.transport.closeChildFD(descriptor)


    def loseConnection(self):
        return self.transport.loseConnection()


    def signalProcess(self, signal):
        return self.transport.signalProcess(signal)


    def getPeer(self):
        return self.transport.getPeer()


    def getHost(self):
        return self.transport.getHost()


    def write(self, data):
        """
        Write to stdin
        """
        self._ch3_receiver(ch3.fd(self.name, 0, data))
        return self.transport.write(data)


    def writeToChild(self, childFD, data):
        self._ch3_receiver(ch3.fd(self.name, childFD, data))
        return self.transport.writeToChild(childFD, data)


    def writeSequence(self, seq):
        for x in seq:
            self._ch3_receiver(ch3.fd(self.name, 0, x))
        return self.transport.writeSequence(seq)



def _spawnDefaultArgs(executable, args=(), env={}, path=None, uid=None,
                      gid=None, usePTY=0):
    """
    I get the defaults for some keyword arguments for a reactor.spawnProcess
    call.
    
    @return: A dictionary with the values that will be used when spawning.
    """
    if env is None:
        env = os.environ
    path = path or os.curdir
    uid = uid or os.geteuid()
    gid = gid or os.getegid()
    return {
        'executable': executable,
        'args': args,
        'env': env,
        'path': path,
        'uid': uid,
        'gid': gid,
        'usePTY': usePTY,
    }


