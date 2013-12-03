"""
Mixins for general-purpose, functional connection testing.
"""

from twisted.internet import defer, protocol
from twisted.python import log
from twisted.web.client import FileBodyProducer

import os
import pipes
from hashlib import md5
from StringIO import StringIO

from mold.transport.common import SimpleProtocol, TriggerInput, AnyString, tee



class TestProtocol(protocol.ProcessProtocol):


    def __init__(self, stdin=None):
        self.done = defer.Deferred()
        self.output = StringIO()
        self.stdin = stdin


    def connectionMade(self):
        if self.stdin is not None:
            log.msg('%r' % (self.stdin,), system='stdin')
            self.transport.write(self.stdin)
            self.transport.write('\x04')
            log.msg('close', system='stdin')
            self.transport.closeStdin()



    def childDataReceived(self, childFD, data):
        log.msg('data received: %r %r' % (childFD, data,))
        self.output.write(data)


    def processEnded(self, reason):
        log.msg('ended', system='process')
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
        proto = TestProtocol(stdin)
        connection.spawnProcess(proto, command)
        yield proto.done
        defer.returnValue(proto.output.getvalue())


    @defer.inlineCallbacks
    def assertOutput(self, command, expected_lines, stdin=None):
        """
        Assert that the output of the command is as expected.
        """
        connection = yield self._getConnection()
        output = yield self.outputOf(connection, command, stdin)
        for line in expected_lines:
            self.assertIn(line, output,
                         "Expected output of\n%s\n\n"
                         "with stdin:\n%r\n\n"
                         "to contain:\n%r\n\n"
                         "but it doesn't:\n%r" % (command, stdin, line, output))


    def test_echo(self):
        """
        You should be able to run echo and get stdout output.
        """
        return self.assertOutput('echo foo', ['foo'])


    def test_stdin(self):
        """
        You should be able to send stdin
        """
        return self.assertOutput(
            "/bin/bash -c 'while read line; do echo $line; done'",
            # XXX this assertion is terrible
            ["foo"],
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

        # verify the hash
        expected_hash = md5(value).hexdigest()
        output = yield self.outputOf(
            connection,
            'md5sum %s' % (tmpfilename,)
        )
        actual_hash = output.strip().split(' ')[0]

        self.assertEqual(expected_hash, actual_hash)


    @defer.inlineCallbacks
    def test_copyFile_specialChars(self):
        """
        If the pathname has special characters, it should still work
        """
        connection = yield self._getConnection()

        # get a temporary filename
        tmpdir = yield self.outputOf(connection,
            "python -c 'import tempfile, sys; sys.stdout.write(tempfile.mkdtemp())'")
        log.msg('tmpdir: %s' % (tmpdir,))
        tmpfile = os.path.join(tmpdir, "andy's frozen - treats")

        # copy it
        value = 'foobarHey'
        contents = StringIO(value)
        producer = FileBodyProducer(contents)
        yield connection.copyFile(tmpfile, producer)

        # make sure it made it
        expected = 'foobarHey'
        output = yield self.outputOf(connection, 'cat %s' % (
                                     pipes.quote(tmpfile),))
        self.assertEqual(output, expected)


    @defer.inlineCallbacks
    def test_passwordPrompt(self):
        """
        A password prompt should be handled well with triggers.
        """
        connection = yield self._getConnection()
        
        triggers = [TriggerInput('answer\r\n', AnyString(['password?']))]
        output = []
        proto = SimpleProtocol(
            lambda data: tee([log.msg(repr(data)), output.append(data)]),
            triggers=triggers)

        # ask for a password
        connection.spawnProcess(
            proto,
            "python -c 'import getpass, sys; sys.stdout.write(getpass.getpass(\"password?\"))'",
        )

        yield proto.done
        self.assertIn('password?', ''.join(output))
        self.assertIn('answer', ''.join(output))
