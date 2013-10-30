from twisted.internet.protocol import ProcessProtocol, Protocol, Factory
from twisted.conch.endpoints import SSHCommandClientEndpoint
from twisted.conch.client.knownhosts import KnownHostsFile, ConsoleUI
from twisted.internet import defer, reactor

from zope.interface import implements

from mold.interface import IConnection, IConnectionMaker
from mold.error import Error

from urlparse import urlparse
from urllib import unquote_plus as unquote

import pipes



class AuthenticationLacking(Error):
    pass



def parseURI(uri):
    """
    Convert a URI string into a dictionary of parts.
    """
    parsed = urlparse(uri)
    password = parsed.password
    if password is not None:
        password = unquote(password)
    return {
        'username': unquote(parsed.username),
        'hostname': unquote(parsed.hostname),
        'port': parsed.port or 22,
        'password': password,
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
        return self.spawnProcess(brute, 'cat > %s' % (pipes.quote(path),))






class _PersistentProtocol(Protocol):


    def __init__(self):
        self.done = defer.Deferred()


    def connectionLost(self, reason):
        self.done.callback(self)




class SSHConnectionMaker(object):
    """
    I make L{SSHConnection}s from URIs.
    """

    implements(IConnectionMaker)


    def __init__(self, askForPassword=None):
        """
        @param askForPassword: Either C{None} if passwords can't be asked for,
            or else a function that takes a string prompt and returns a
            (potentially deferred) password.
        """
        self.askForPassword = askForPassword


    def getConnection(self, uri):
        parsed = parseURI(uri)
        if parsed['password'] is None:
            if self.askForPassword:
                d = defer.maybeDeferred(self.askForPassword, 'Password?\n')
                return d.addCallback(self._gotPassword, parsed)
            else:
                return defer.fail(AuthenticationLacking(
                        "You must supply either a password or an identity."))
        return self._connect(parsed)


    def _gotPassword(self, password, kwargs):
        kwargs = kwargs.copy()
        kwargs['password'] = password
        return self._connect(kwargs)


    def _connect(self, params):
        ep = SSHCommandClientEndpoint.newConnection(
                reactor,
                b'/bin/cat',
                params['username'],
                params['hostname'],
                port=params['port'],
                password=params['password'],
                agentEndpoint=None,
                knownHosts=None)
        factory = Factory()
        factory.protocol = _PersistentProtocol
        return ep.connect(factory).addCallback(self._connected)


    def _connected(self, proto):
        return SSHConnection(proto)


