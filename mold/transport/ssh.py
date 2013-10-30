from twisted.internet.protocol import ProcessProtocol, Protocol, Factory
from twisted.conch.endpoints import SSHCommandClientEndpoint
from twisted.internet import defer, reactor

from zope.interface import implements

from mold.interface import IConnection, IConnectionMaker

from urlparse import urlparse
from urllib import unquote_plus as unquote




def parseURI(uri):
    """
    Convert a URI string into a dictionary of parts.
    """
    parsed = urlparse(uri)
    return {
        'username': unquote(parsed.username),
        'hostname': unquote(parsed.hostname),
        'port': parsed.port or 22,
        'password': unquote(parsed.password or ''),
    }



class _CommandProtocol(Protocol):

    output_childFD = 1


    def __init__(self, process_protocol):
        self.done = defer.Deferred()
        self.process_protocol = process_protocol


    def connectionMade(self):
        self.process_protocol.makeConnection(self)


    def connectionLost(self, reason):
        self.process_protocol.processEnded(reason)
        self.done.callback(self)


    def dataReceived(self, data):
        self.process_protocol.childDataReceived(self.output_childFD, data)


    # ITransport

    def write(self, data):
        self.transport.write(data)


    def closeStdin(self):
        self.transport.conn.sendEOF(self.transport)


class _StdinConsumer(ProcessProtocol):
    """
    I write a file to stdin from a producer.
    """

    def __init__(self, producer):
        self.producer = producer

    def connectionMade(self):
        d = self.producer.startProducing(self)
        d.addCallback(self._doneProducing)


    def write(self, data):
        self.transport.write(data)


    def _doneProducing(self, _):
        self.transport.closeStdin()



class SSHConnection(object):
    """
    XXX
    """

    implements(IConnection)


    def __init__(self, master_proto):
        """
        @param master_proto: XXX
        """
        self.master_proto = master_proto


    def close(self):
        self.master_proto.transport.loseConnection()
        return self.master_proto.done


    def spawnProcess(self, protocol, command):
        factory = Factory()
        factory.protocol = lambda: _CommandProtocol(protocol)
        e = SSHCommandClientEndpoint.existingConnection(
                self.master_proto.transport.conn, command)
        d = e.connect(factory)
        return d.addCallback(self._commandStarted)


    def _commandStarted(self, proto):
        return proto.done


    def copyFile(self, path, producer):
        """
        XXX
        """
        # XXX brutish version
        brute = _StdinConsumer(producer)
        return self.spawnProcess(brute, 'cat > %s' % (path,))






class _PersistentProtocol(Protocol):


    def __init__(self):
        self.done = defer.Deferred()


    def connectionLost(self, reason):
        self.done.callback(self)




class SSHConnectionMaker(object):
    """
    XXX
    """

    implements(IConnectionMaker)


    def getConnection(self, uri):
        parsed = parseURI(uri)
        ep = SSHCommandClientEndpoint.newConnection(
                reactor,
                b'/bin/cat',
                parsed['username'],
                parsed['hostname'],
                port=parsed['port'],
                password=parsed['password'],
                agentEndpoint=None,
                knownHosts=None)
        factory = Factory()
        factory.protocol = _PersistentProtocol
        return ep.connect(factory).addCallback(self._connected)


    def _connected(self, proto):
        return SSHConnection(proto)


