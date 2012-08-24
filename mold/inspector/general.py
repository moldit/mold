from twisted.internet import reactor, defer, protocol

from mold.error import Error

from twisted.python.filepath import FilePath

import sys
import json
import os

from collections import defaultdict


class UnknownResource(Error): pass



class MyProto(protocol.ProcessProtocol):


    def __init__(self, stdin):
        self.stdin = stdin
        self.done = defer.Deferred()
        self.output = defaultdict(lambda: [])

    def connectionMade(self):
        self.transport.write(self.stdin)
        self.transport.closeStdin()

    def childDataReceived(self, childFD, data):
        if childFD == 1:
            self.outReceived(data)
        elif childFD == 2:
            self.errReceived(data)
        elif childFD == 3:
            self.ctlReceived(data)


    def outReceived(self, data):
        print 'out: %r' % data
        self.output['out'].append(data)


    def errReceived(self, data):
        print 'err: %r' % data
        sys.stderr.write(data)


    def ctlReceived(self, data):
        print 'ctl: %r' % data
#        ctl('child: %s' % data)        

    def processEnded(self, reason):
        self.done.callback(reason.value.exitCode)


def out(msg):
    sys.stdout.write(msg)


def err(msg):
    sys.stderr.write(msg)


def ctl(msg):
    try:
        os.write(3, msg)
    except OSError as e:
        # if no one's listening for this stuff, it's okay; their loss.
        pass




class Inspector:
    """
    XXX
    """
    
    def __init__(self, inspector_root):
        """
        @param inspectors: path where all inspector files are
        """
        self.root = FilePath(inspector_root)


    @defer.inlineCallbacks
    def inspect(self, resources):
        """
        XXX
        """
        singleton = False
        if type(resources) == type({}):
            singleton = True
            resources = [resources]
        
        res = []
        
        for resource in resources:
            kind = resource['kind']
            handler = self.root.child(kind)
            if not handler.exists():
                # XXX log this?
                sys.stderr.write('no handler for resource kind %s\n' % kind)
                continue
            proto = MyProto(json.dumps(resource))
            ctl('spawn: %s\n' % str(handler.path))
            reactor.spawnProcess(proto, '/bin/bash',
                                 ['/bin/bash', str(handler.path)],
                                 env=None,
                                 childFDs={
                                    0: 'w',
                                    1: 'r',
                                    2: 'r',
                                    3: 'r',
                                 })
            r = yield proto.done
            res.append(json.loads(''.join(proto.output['out'])))
        
        if singleton:
            res = res[0]
        
        defer.returnValue(res)


