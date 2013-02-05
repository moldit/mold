# -*- test-case-name: mold.test.test_process -*-
"""
XXX
"""

__all__ = ['SimpleProtocol', 'Channel3Protocol', 'spawnChannel3']

from twisted.internet import protocol, defer, interfaces, reactor
from twisted.python.runtime import platform
from twisted.python.filepath import FilePath

from zope.interface import implements

import os

from mold import ch3



class SimpleProtocol(protocol.ProcessProtocol):
    """
    I write a chunk of stdin to the process and read the stdout and stderr out.
    
    @param stdout: A string of all stdout encountered so far
    @param stderr: A string of all stderr encountered so far
    @param done: A C{Deferred} which will fire with me on success (exit code 0)
        and an error on failure.
    """
    
    
    def __init__(self, stdin):
        """
        @ivar stdin: standard in to write immediately on connection.
        """
        self.stdin = stdin
        self.stdout = ''
        self.stderr = ''
        self.done = defer.Deferred()


    def connectionMade(self):
        self.transport.write(self.stdin)
        self.transport.closeStdin()


    def childDataReceived(self, childfd, data):
        if childfd == 1:
            self.stdout += data
        elif childfd == 2:
            self.stderr += data


    def processEnded(self, status):
        if status.value.exitCode == 0:
            self.done.callback(self)
        else:
            self.done.errback(status)



class Channel3Protocol(protocol.ProcessProtocol):
    """
    I am a Channel3 logging protocol and also an C{IProcessTransport}.
    
    Use me like this::
    
        proto = MyProcessProtocol()
        log = []
        logger = Channel3Protocol('myprocess', log.append, proto)
        reactor.spawnProcess(logger, ...)
    
    @ivar done: A C{Deferred} which will fire when the process has 
        finished.
    @ivar started: A C{Deferred} which fires on my L{connectionMade}.
    """
    
    implements(interfaces.IProcessTransport)
    _pid = None
    
    
    def __init__(self, channel3_receiver, sub_proto):
        """
        @ivar channel3_receiver: A function that will be called with
            L{Messages<ch3.Message>} when interesting log events happen.

        @ivar sub_proto: a C{ProcessProtocol} that will actually do interesting
            things with the stdout and write interesting stdin.  Actually,
            there's no guarantee that either input or output will be
            interesting.
        """
        self.done = defer.Deferred()
        self.started = defer.Deferred()
        self.sub_proto = sub_proto
        self._ch3_receiver = channel3_receiver


    def connectionMade(self):
        self._pid = self.transport.pid
        self.started.callback(self)
        self.sub_proto.makeConnection(self)


    def childDataReceived(self, childfd, data):
        self._ch3_receiver(ch3.ProcessStream(self.pid, childfd, data))
        self.sub_proto.childDataReceived(childfd, data)


    def inConnectionLost(self):
        self.sub_proto.inConnectionLost()


    def outConnectionLost(self):
        self.sub_proto.outConnectionLost()


    def errConnectionLost(self):
        self.sub_proto.errConnectionLost()


    def processExited(self, status):
        self.sub_proto.processExited(status)


    def processEnded(self, status):
        """
        XXX
        """
        self._ch3_receiver(ch3.ProcessEnded(self.pid,
                                    status.value.exitCode,
                                    status.value.signal))
        self.sub_proto.processEnded(status)
        self.done.callback(status)


    # IProcessTransport
    
    @property
    def pid(self):
        return self._pid
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
        self._ch3_receiver(ch3.ProcessStream(self.pid, 0, data))
        return self.transport.write(data)


    def writeToChild(self, childFD, data):
        self._ch3_receiver(ch3.ProcessStream(self.pid, childFD, data))
        return self.transport.writeToChild(childFD, data)


    def writeSequence(self, seq):
        for x in seq:
            self._ch3_receiver(ch3.ProcessStream(self.pid, 0, x))
        return self.transport.writeSequence(seq)



def _spawnDefaultArgs(executable, args=(), env={}, path=None, uid=None,
                      gid=None, usePTY=0):
    """
    I get the defaults for some keyword arguments for a reactor.spawnProcess
    call.
    
    @return: A dictionary with the values that will be used when spawning.
    """
    if env is None:
        env = dict(os.environ)
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



def spawnChannel3(ch3_receiver, protocol, executable, args=(), env={},
                  path=None, uid=None, gid=None, usePTY=0):
    """
    Spawn a process with Channel3 logging enabled.
    
    @param name: Name of the process as will appear in logs.
    @param ch3_receiver: A function of one argument that will accept
        L{Messages<ch3.Message>}.
    
    @param protocol: C{ProcessProtocol} instance that will handle stdin/out/err.
    
    @param **kwargs: See C{reactor.spawnProcess}.
    """
    p = Channel3Protocol(ch3_receiver, protocol)  
    kw = _spawnDefaultArgs(executable, args, env, path, uid, gid, usePTY)

    # log it    
    def logSpawn(p):
        ch3_receiver(ch3.ProcessStarted(
            os.getpid(),
            p.pid,
            kw['executable'],
            kw['args'],
            kw['env'],
            kw['path'],
            kw['uid'],
            kw['gid'],
            kw['usePTY'],
        ))
        return p
    p.started.addCallback(logSpawn)

    
    # spawn it
    childFDs = {
        0: 'w',
        1: 'r',
        2: 'r',
        3: 'r',
    }
    reactor.spawnProcess(p, executable, args, env, path, uid, gid, usePTY,
                         childFDs)
    return p


