"""
Mixins for general-purpose, functional connection testing.
"""

from twisted.internet import defer, protocol
from twisted.python import log

from StringIO import StringIO


class SimpleProtocol(protocol.ProcessProtocol):


    def __init__(self):
        self.done = defer.Deferred()
        self.output = StringIO()


    def childDataReceived(self, childFD, data):
        log.msg('data received: %r %r' % (childFD, data,))
        self.output.write(data)


    def processEnded(self, reason):
        self.done.callback(self)



class FunctionalConnectionTestMixin(object):

    timeout = 2


    def getConnection(self):
        raise NotImplementedError("You must implement getConnection in order "
                                  "to use the FunctionalConnectionTestMixin.")


    @defer.inlineCallbacks
    def outputOf(self, connection, command):
        proto = SimpleProtocol()
        connection.spawnProcess(proto, command)
        yield proto.done
        defer.returnValue(proto.output.getvalue())


    @defer.inlineCallbacks
    def assertOutput(self, command, expected):
        """
        Assert that the output of the command is as expected.
        """
        connection = yield self.getConnection()
        output = yield self.outputOf(connection, command)
        self.assertEqual(output, expected,
                         "Expected output of\n%s\n\n"
                         "to be\n%r\n\n"
                         "not\n%r" % (command, expected, output))


    def test_echo(self):
        """
        You should be able to run echo and get stdout output.
        """
        return self.assertOutput('echo foo', 'foo\n')





