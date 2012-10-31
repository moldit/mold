"""
XXX
"""

from twisted.internet import protocol, defer
from twisted.protocols.basic import NetstringReceiver


from mold.log import MessageFactory
from mold import ch3

import json
import uuid
import os
import re



class NotFinished(Exception): pass



class Channel3Protocol(protocol.ProcessProtocol):

    
    
    def __init__(self, name, channel3_receiver):
        self.name = name
        self._ch3_receiver = channel3_receiver
        
        # some initialization happens in makeConnection
        self._ch3_netstring = NetstringReceiver()
        self._ch3_netstring.makeConnection(None)
        self._ch3_netstring.stringReceived = self._ch3DataReceived


    def childDataReceived(self, childfd, data):
        if childfd == 3:
            self._ch3_netstring.dataReceived(data)
        else:
            self._ch3_receiver(ch3.fd(self.name, childfd, data))


    def _ch3DataReceived(self, data):
        name, key, val = ch3.decode(data)
        name = '.'.join([self.name, name])
        self._ch3_receiver(ch3.encode((name, key, val)))


    def write(self, data):
        """
        Write to stdin
        """
        self._ch3_receiver(ch3.fd(self.name, 0, data))
        self.transport.write(data)



class NetstringBuffer:


    state = 'length'
    
    r_length = re.compile('((.*?)([0-9]+):)')
    r_nonnum = re.compile('([^0-9]+)')

    
    def __init__(self, goodstring, badstring=None):
        """
        @param goodstring: Function that will be called once per good string
            encountered.
        @param badstring: Function that will be called with each malformed
            string as it's encountered.
        """
        self._buffer = ''
        self.length = ''
        self.string = ''
        self.goodstring = goodstring
        self.badstring = badstring or (lambda x:None)


    def dataReceived(self, data):
        self._buffer += data
        self.parseBuffer()


    def parseBuffer(self):
        while self._buffer:
            m = getattr(self, 'parse_'+self.state)
            try:
                self.state = m()
            except NotFinished:
                break

    def parse_length(self):
        m = self.r_length.match(self._buffer)
        if not m:
            m = self.r_nonnum.match(self._buffer)
            if m:
                bad = m.groups()[0]
                self._buffer = self._buffer[len(bad):]
                self.badstring(bad)
            raise NotFinished()
        
        whole, bad, good = m.groups()
        while len(good) > 1 and good[0] == '0':
            bad += '0'
            good = good[1:]
        if bad:
            self.badstring(bad)
        self.length = long(good)
        self._buffer = self._buffer[len(whole):]
        return 'string'


    def parse_string(self):
        remaining = self.length - len(self.string)
        self.string += self._buffer[:remaining]
        self._buffer = self._buffer[remaining:]
        if len(self.string) == self.length:
            # done with string
            if not self._buffer:
                return 'string'
            elif self._buffer[0] == ',':
                self._buffer = self._buffer[1:]
                self.goodstring(self.string)
                self.string = ''
                self.length = ''
                return 'length'
            else:
                m = self.r_nonnum.match(self._buffer)
                bad = ('%s:'% self.length) + self._buffer
                self.badstring(self._buffer)
                self.string = ''
                self.length = ''
                return 'length'
        return 'string'
        


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




