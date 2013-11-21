from twisted.trial.unittest import TestCase
from twisted.python.filepath import FilePath
from twisted.python import log
from twisted.internet import utils, defer, reactor
from twisted.internet.protocol import ProcessProtocol


from mold.util import script_root
from mold.netstring import NetstringReader, KeyPairReader



class fdplexMixin(object):

    timeout = 2

    def getScriptPath(self):
        raise NotImplementedError("You must implement getScriptPath "
                                  "to use the fdplexMixin test mixin.")


    def parseStream(self, out):
        data = {}
        def receivePair((key, value)):
            if key in data:
                data[key] += value
            else:
                data[key] = value

        kp_reader = KeyPairReader(receivePair)
        ns_reader = NetstringReader(kp_reader.stringReceived)
        ns_reader.dataReceived(out)
        return data


    @defer.inlineCallbacks
    def runnableScript(self):
        # copy it to a temporary place
        path = yield self.getScriptPath()
        fp = FilePath(path)
        tmpdir = FilePath(self.mktemp())
        tmpdir.makedirs()
        script = tmpdir.child('fdplex-script')
        script.setContent(fp.getContent())
        defer.returnValue(script.path)


    @defer.inlineCallbacks
    def runProcess(self, executable, args):
        """
        Run a process, and return the out, err, rc and parsed data.
        """
        out, err, rc = yield utils.getProcessOutputAndValue(executable, args)
        log.msg('out: %r' % (out,))
        log.msg('err: %r' % (err,))
        log.msg('rc: %r' % (rc,))
        data = self.parseStream(out)
        defer.returnValue((out, err, rc, data))


    @defer.inlineCallbacks
    def test_returnCode_fail(self):
        """
        The fdplex script should indicate the return code of the script.
        """
        fdplex = yield self.runnableScript()
        
        # script to wrap
        child = FilePath(self.mktemp())
        child.setContent(
            '#!/bin/bash\n'
            'exit 1\n'
        )
        
        out, err, rc, data = yield self.runProcess(fdplex, [child.path])

        self.assertEqual(rc, 1, "Should fail because child failed")
        self.assertEqual(err, '', "Should not emit any stderr")
        self.assertEqual(data['rc'], '1', "Should indicate return code")


    @defer.inlineCallbacks
    def test_returnCode_success(self):
        """
        The fdplex script should indicate the return code and mirror it.
        """
        fdplex = yield self.runnableScript()

        child = FilePath(self.mktemp())
        child.setContent(
            '#!/bin/bash\n'
            'exit 0\n'
        )
        
        out, err, rc, data = yield self.runProcess(fdplex, [child.path])
        
        self.assertEqual(rc, 0, "Should succeed because child succeeded")
        self.assertEqual(err, '', "Should not emit any stderr")
        self.assertEqual(data['rc'], '0', "Should indicate return code")


    @defer.inlineCallbacks
    def test_stdout(self):
        """
        Stdout should be wrapped in netstrings.
        """
        fdplex = yield self.runnableScript()

        child = FilePath(self.mktemp())
        child.setContent(
            '#!/bin/bash\n'
            'echo foo\n'
        )
        
        out, err, rc, data = yield self.runProcess(fdplex, [child.path])
        
        self.assertEqual(data['fd1'], 'foo\n', "Should capture stdout")


    @defer.inlineCallbacks
    def test_stderr(self):
        """
        Stderr of the child should be wrapped in netstrings and written to the
        parent's stdout.
        """
        fdplex = yield self.runnableScript()

        child = FilePath(self.mktemp())
        child.setContent(
            '#!/bin/bash\n'
            'echo foo >&2\n'
        )
        
        out, err, rc, data = yield self.runProcess(fdplex, [child.path])
        
        self.assertEqual(data['fd2'], 'foo\n', "Should capture stderr")


    @defer.inlineCallbacks
    def test_terminal(self):
        """
        Input asked of the terminal should come out stderr.
        """
        fdplex = yield self.runnableScript()

        class Proto(ProcessProtocol):

            def __init__(self, input_responses=[]):
                """
                @param input_responses: A list of strings to be
                    written in response to data being received.
                """
                self.data = {
                    1: '',
                    2: '',
                }
                self.input_responses = input_responses
                self.done = defer.Deferred()

            def childDataReceived(self, childFd, data):
                self.data[childFd] += data
                if self.input_responses:
                    input_data = self.input_responses.pop(0)
                    self.transport.write(input_data)

            def processEnded(self, reason):
                print dir(reason)
                self.done.callback(reason.value)


        child = FilePath(self.mktemp())
        child.setContent(
            '#!/usr/bin/env python\n'
            'import getpass\n'
            'value = getpass.getpass("password?")\n'
            'print value\n'
        )

        proto = Proto(['joe'])
        reactor.spawnProcess(proto, fdplex, [fdplex, child], usePty=True)

        result = yield proto.done
        self.fail('writ me')







class pythonfdplexTest(TestCase, fdplexMixin):


    def getScriptPath(self):
        return script_root.child('fdplex.py').path



class gofdplexTest(TestCase, fdplexMixin):


    def getScriptPath(self):
        return script_root.child('go-fdplex').path

