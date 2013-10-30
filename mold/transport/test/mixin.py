"""
Mixins for general-purpose, functional connection testing.
"""

from twisted.internet import defer, protocol
from twisted.python import log
from twisted.web.client import FileBodyProducer

from StringIO import StringIO



class SimpleProtocol(protocol.ProcessProtocol):


    def __init__(self, stdin=None):
        self.done = defer.Deferred()
        self.output = StringIO()
        self.stdin = stdin


    def connectionMade(self):
        if self.stdin is not None:
            log.msg('stdin: %r' % (self.stdin,))
            self.transport.write(self.stdin)
            self.transport.closeStdin()


    def childDataReceived(self, childFD, data):
        log.msg('data received: %r %r' % (childFD, data,))
        self.output.write(data)


    def processEnded(self, reason):
        self.done.callback(self)



class FunctionalConnectionTestMixin(object):

    timeout = 1


    def getConnection(self):
        raise NotImplementedError("You must implement getConnection in order "
                                  "to use the FunctionalConnectionTestMixin.")


    @defer.inlineCallbacks
    def _getConnection(self):
        conn = yield self.getConnection()
        self.addCleanup(conn.close)
        defer.returnValue(conn)


    @defer.inlineCallbacks
    def outputOf(self, connection, command, stdin=None):
        log.msg('Running: %r' % (command,))
        proto = SimpleProtocol(stdin)
        connection.spawnProcess(proto, command)
        yield proto.done
        defer.returnValue(proto.output.getvalue())


    @defer.inlineCallbacks
    def assertOutput(self, command, expected, stdin=None):
        """
        Assert that the output of the command is as expected.
        """
        connection = yield self._getConnection()
        output = yield self.outputOf(connection, command, stdin)
        self.assertEqual(output, expected,
                         "Expected output of\n%s\n\n"
                         "with stdin:\n%r\n\n"
                         "to be:\n%r\n\n"
                         "not:\n%r" % (command, stdin, expected, output))


    def test_echo(self):
        """
        You should be able to run echo and get stdout output.
        """
        return self.assertOutput('echo foo', 'foo\n')


    def test_stdin(self):
        """
        You should be able to send stdin
        """
        return self.assertOutput(
            "/bin/bash -c 'while read line; do echo $line; done'",
            "foo\n",
            stdin="foo\n")


    @defer.inlineCallbacks
    def test_copyFile(self):
        """
        You should be able to copy a file onto the machine
        """
        connection = yield self._getConnection()

        # get a temporary filename
        tmpfilename = yield self.outputOf(connection,
            "python -c 'import tempfile, sys; sys.stdout.write(tempfile.mkstemp()[1])'")

        # copy it
        value = 'foobar\x00\x01Hey'
        contents = StringIO(value)
        producer = FileBodyProducer(contents)
        yield connection.copyFile(tmpfilename, producer)

        # make sure it made it
        expected = ''.join(('0'+hex(ord(c))[2:])[-2:] for c in value) + '\n'
        output = yield self.outputOf(connection, 'xxd -p %s' % (tmpfilename,))
        self.assertEqual(output, expected)


        






