# -*- test-case-name: mold.test.test_process -*-
"""
XXX
"""

from twisted.internet import protocol, defer
from twisted.protocols.basic import NetstringReceiver


from mold import ch3

import json
import uuid
import os
import re



class Channel3Protocol(protocol.ProcessProtocol):
    """
    XXX
    
    @ivar done: A C{Deferred} which will fire when the process has 
        finished.
    """
    
    
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


    def write(self, data):
        """
        Write to stdin
        """
        self._ch3_receiver(ch3.fd(self.name, 0, data))
        self.transport.write(data)


    def processEnded(self, status):
        """
        XXX
        """
        self._ch3_receiver(ch3.exit(self.name,
                                    status.value.exitCode,
                                    status.value.signal))
        self.done.callback(status)



def spawnLogged(reactor, proto, executable, args=(), env={}, path=None,
                uid=None, gid=None, usePTY=False):
    fds = {
        0: 'w',
        1: 'r',
        2: 'r',
        3: 'r',
    }
    log_args = {
        'executable': executable,
        'args': args,
        'env': env,
        'path': path,
        'uid': uid,
        'gid': gid,
        'usePTY': usePTY,
    }
    proto.logSpawn(**log_args)
    reactor.spawnProcess(proto, executable, args, env, path, usePTY=usePTY,
                         childFDs=fds)



class LoggingProtocol(protocol.ProcessProtocol):
    """
    I am a process protocol that will log to a historian.
    
    @ivar label: Uniqueish label for the spawned process.  Used in sending log
        data to the historian.
    
    @ivar done: A C{Deferred} which fires when the process is done.
    """
    
    label = None
    
    done = None

    
    def __init__(self, label=None, stdin=None, stdout=None, stderr=None,
                 control=None, msg_factory=None):
        """      
        @param label: String label identifying the process for which I am a
            protocol.
        
        @type stdin: string
        @param stdin: string to send process as soon as it's connected.  Note
            that this will close stdin as soon as the data is sent.  If you do
            not want this behavior, please call L{write} and close stdin with
            L{closeStdin()} when you're done.
        
        @param stdout: Function that will be given each string of stdout
            received by me.
        @param stderr: Function that will be given each string of stderr
            received by me.
        @param control: Function that will be given each string of control data
            received by me.
        """
        self.label = label or str(uuid.uuid4().bytes).encode('base64').strip()
        self.msg_factory = msg_factory or MessageFactory()
        self.done = defer.Deferred()

        self._stdin = stdin
        self._stdout = stdout or (lambda x:None)
        self._stderr = stderr or (lambda x:None)
        self._control = control or (lambda x:None)


    def logSpawn(self, executable, args=(), env={}, path=None, uid=None,
                 gid=None, usePTY=False):
        """
        Log how this process was spawned.
        """
        path = path or os.path.abspath(os.curdir)
        uid = uid or os.geteuid()
        gid = gid or os.getegid()
        msg = self.msg_factory.processSpawned(self.label, executable, args, env,
                                             path, uid, gid, usePTY)
        self.sendControl(msg)


    def connectionMade(self):
        """
        As soon as I am connected to the process.
        """
        if self._stdin is not None:
            self.write(self._stdin)
            self.closeStdin()


    def write(self, data):
        """
        Write data to the process' stdin.
        """
        self.sendControl(self.msg_factory.fd(self.label, 0, data))
        self.transport.write(data)


    def closeStdin(self):
        """
        Close the process' stdin
        """
        self.transport.closeStdin()

    
    def childDataReceived(self, childfd, data):
        """
        Called when any data is received on any of my child's file descriptors.
        """
        if childfd == 1:
            self.outReceived(data)
        elif childfd == 2:
            self.errReceived(data)
        elif childfd == 3:
            self.ctlReceived(data)

    def sendControl(self, message):
        """
        Send control message to handler.
        
        @param message: An entire message (no chunks).
        """
        self._control(message)


    def ctlReceived(self, data):
        """
        Control statement received.
        
        @param data: A portion/entire netstring, typically with a JSON payload.
        """
        raise NotImplementedError('foo')
        self.sendControl(self.msg_factory.fd(self.label, 3, data))
        self._control(data)


    def outReceived(self, data):
        """
        Standard output from child process received.
        
        @param data: a string
        """
        self.sendControl(self.msg_factory.fd(self.label, 1, data))
        self._stdout(data)


    def errReceived(self, data):
        """
        Standard error from child process received.
        
        @param data: a string
        """
        self.sendControl(self.msg_factory.fd(self.label, 2, data))
        self._stderr(data)


    def processEnded(self, status):
        self.sendControl(self.msg_factory.processEnded(
            self.label, status.value.exitCode, status.value.signal))
        if status.value.exitCode != 0:
            self.done.errback(status)
        else:
            self.done.callback((status.value.exitCode, status.value.signal))




