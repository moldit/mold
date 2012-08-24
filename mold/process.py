"""
XXX
"""

from twisted.internet import protocol, defer


import json
import uuid



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
                 control=None):
        """      
        @param label: String label identifying the process for which I am a
            protocol.
        
        @type stdin: string
        @param stdin: string to send process as soon as it's connected.  Note
            that this will close stdin as soon as the data is sent.  If you do
            not want this behavior, please call my C{transport.write} method
            and close stdin with C{transport.closeStdin()} when you're done.
        
        @param stdout: Function that will be given each string of stdout
            received by me.
        @param stderr: Function that will be given each string of stderr
            received by me.
        @param control: Function that will be given each string of control data
            received by me.
        """
        self.label = label or str(uuid.uuid4().bytes).encode('base64')
        self.done = defer.Deferred()

        self._stdin = stdin
        self._stdout = stdout or (lambda x:None)
        self._stderr = stderr or (lambda x:None)
        self._control = control or (lambda x:None)


    def connectionMade(self):
        """
        As soon as I am connected to the process.
        """
        if self._stdin is not None:
            self.transport.write(self._stdin)
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
        self._stdout(data)
        self.ctlReceived(json.dumps({
            'fd': 1,
            'm': data,
            'lab': self.label,
        }))


    def errReceived(self, data):
        """
        Standard error from child process received.
        
        @param data: a string
        """
        self._stderr(data)
        self.ctlReceived(json.dumps({
            'fd': 2,
            'm': data,
            'lab': self.label,
        }))


    def processEnded(self, status):
        self.done.callback((status.value.exitCode, status.value.signal))




