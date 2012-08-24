"""
XXX
"""

from twisted.internet import protocol


import json
import uuid



class LoggingProtocol(protocol.ProcessProtocol):
    """
    I am a process protocol that will log to a historian.
    
    @ivar label: Uniqueish label for the spawned process.  Used in sending log
        data to the historian.
    """
    
    label = None

    
    def __init__(self, historian=None):
        """
        @param historian: A function that will be given strings of control data
            as they are received by this protocol.
        """
        self.historian = historian or (lambda x:None)
        self.label = str(uuid.uuid4()).encode('hex')
    
    
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
        self.historian(data)


    def outReceived(self, data):
        """
        Standard output from child process received.
        
        @param data: a string
        """
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
        self.ctlReceived(json.dumps({'fd':2, 'm':data}))
