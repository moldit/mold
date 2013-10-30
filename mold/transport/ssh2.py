from twisted.internet.protocol import Protocol, Factory
from twisted.conch.endpoints import SSHCommandClientEndpoint
from twisted.conch.ssh.keys import EncryptedKeyError, Key
from twisted.internet import defer, stdio
from twisted.protocols import basic
from twisted.internet.task import react
from twisted.python import log

import getpass
from os import linesep as delimiter
import sys


details = {
    'USER': 'dev',
    'PASSWORD': None,
    'HOST': '10.1.15.7',
    'PORT': 22,
}

def readKey(path):
    try:
        return Key.fromFile(path)
    except EncryptedKeyError:
        passphrase = getpass.getpass("%r keyphrase: " % (path,))
        return Key.fromFile(path, passphrase=passphrase)


class MyProtocol(Protocol):


    def connectionMade(self):
        #print 'connection made'
        self.finished = defer.Deferred()


    def dataReceived(self, data):
        print 'data:%r' % (data,)


    def connectionLost(self, reason):
        #print 'connection lost: %s' % (reason,)
        self.finished.callback(None)


class StdinProto(basic.LineReceiver):

    delimiter = delimiter


    def __init__(self, ssh_conn):
        self.ssh_conn = ssh_conn
        self.current_proto = None

    def connectionMade(self):
        self.finished = defer.Deferred()
        self.transport.write('>>> ')

    def lineReceived(self, line):
        #self.sendLine('Executing ' + line)
        if self.current_proto:
            self.writeToCurrentProto(line)
        else:
            self.executeNewCommand(line)


    def writeToCurrentProto(self, line):
        data = line + self.delimiter
        print 'write:%r' % (line,)
        if line == 'EOF':
            print self.current_proto.transport
            print self.current_proto.transport.conn.channelsToRemoteChannel
            self.current_proto.transport.conn.sendEOF(self.current_proto.transport)
            #self.current_proto.transport.loseConnection()
        else:
            self.current_proto.transport.write(data)


    def executeNewCommand(self, line):
        factory = Factory()
        factory.protocol = MyProtocol

        e = SSHCommandClientEndpoint.existingConnection(self.ssh_conn,
                                                        line.strip())
        d = e.connect(factory)
        d.addCallback(self.protoStarted)


    def protoStarted(self, proto):
        self.current_proto = proto
        print dir(proto.transport)
        print dir(proto.transport.conn)
        proto.finished.addBoth(self.protoDone)


    def protoDone(self, ignore):
        self.current_proto = None


    def connectionLost(self, reason):
        self.finished.callback(None)


def main(reactor):
    ep = SSHCommandClientEndpoint.newConnection(
        reactor, b'/bin/cat',
        details['USER'],
        details['HOST'],
        port=details['PORT'],
        password=details['PASSWORD'],
        agentEndpoint=None,
        knownHosts=None)
    factory = Factory()
    factory.protocol = MyProtocol

    d = ep.connect(factory)


    def gotConnection(proto):
        # stdio interface
        stdio_proto = StdinProto(proto.transport.conn)
        stdio.StandardIO(stdio_proto)

        # factory = Factory()
        # factory.protocol = MyProtocol

        # e = SSHCommandClientEndpoint.existingConnection(conn, b"/bin/echo hey")
        # return e.connect(factory).addCallback(lambda proto: proto.finished)
        return stdio_proto.finished

    return d.addCallback(gotConnection)

if __name__ == '__main__':
    log.startLogging(sys.stdout)
    details['PASSWORD'] = getpass.getpass('Password: ')
    react(main)
