"""
XXX
"""

from twisted.internet import protocol, defer


from mold.log import MessageFactory

import json
import uuid
import os



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
        self.label = label or str(uuid.uuid4().bytes).encode('base64')
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
        self.ctlReceived(msg)


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
        self.ctlReceived(self.msg_factory.fd(self.label, 0, data))
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


    def ctlReceived(self, data):
        """
        Control statement received.
        
        @param data: A string, typically JSON.
        """
        self._control(data)


    def outReceived(self, data):
        """
        Standard output from child process received.
        
        @param data: a string
        """
        self.ctlReceived(self.msg_factory.fd(self.label, 1, data))
        self._stdout(data)


    def errReceived(self, data):
        """
        Standard error from child process received.
        
        @param data: a string
        """
        self.ctlReceived(self.msg_factory.fd(self.label, 2, data))
        self._stderr(data)


    def processEnded(self, status):
        self.ctlReceived(self.msg_factory.processEnded(
            self.label, status.value.exitCode, status.value.signal))
        if status.value.exitCode != 0:
            self.done.errback(status)
        else:
            self.done.callback((status.value.exitCode, status.value.signal))




