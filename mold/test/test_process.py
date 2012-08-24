from twisted.trial.unittest import TestCase
from twisted.test.proto_helpers import StringTransport
from twisted.internet import reactor
from twisted.python.filepath import FilePath


import json


from mold.process import LoggingProtocol



class LoggingProtocolTest(TestCase):


    timeout = 1


    def test_defaults(self):
        """
        The LoggingProtocol should generate a uuid.
        """
        proto = LoggingProtocol()
        self.assertNotEqual(proto.label, None)
        

    def test_init(self):
        """
        L{LoggingProtocol} should accept a label.
        """
        proto = LoggingProtocol(label='foo')
        self.assertEqual(proto.label, 'foo')


    def test_done(self):
        """
        The protocol should have a C{done} Deferred which fires with the exit
        code when it's done.
        """
        proto = LoggingProtocol()
        self.assertFalse(proto.done.called)        
        reactor.spawnProcess(proto, '/bin/echo', ['echo', 'foo'])
        
        def check(response):
            exitcode, signal = response
            self.assertEqual(exitcode, 0)
            self.assertEqual(signal, None)
            
        return proto.done.addCallback(check)


    def test_done_error(self):
        """
        The protocol should report any signal used on the process
        """
        script = FilePath(self.mktemp())
        script.setContent('sleep 500')
               
        proto = LoggingProtocol()
        
        # kill the process as soon as it's connected
        def connectionMade():
            proto.transport.signalProcess(9)
        proto.connectionMade = connectionMade

        reactor.spawnProcess(proto, '/bin/bash', ['bash', script.path])
        
        def cb(response):
            self.fail('Should have errbacked: %r' % (response,))
        
        def eb(response):
            self.assertNotEqual(response.value.exitCode, 0)
            self.assertEqual(response.value.signal, 9)
        
        return proto.done.addCallbacks(cb, eb)


    def test_childDataReceived(self):
        """
        Depending on the channel, the corresponding method should be called.
        """
        called = []
        proto = LoggingProtocol()
        
        proto.outReceived = lambda x:called.append(('out', x))
        proto.errReceived = lambda x:called.append(('err', x))
        proto.ctlReceived = lambda x:called.append(('ctl', x))
        
        proto.childDataReceived(1, 'foo')
        self.assertEqual(called, [('out', 'foo')], "1 = stdout")
        
        called.pop()
        proto.childDataReceived(2, 'bar')
        self.assertEqual(called, [('err', 'bar')], "2 = stderr")
        
        called.pop()
        proto.childDataReceived(3, 'wow')
        self.assertEqual(called, [('ctl', 'wow')], "3 = control")


    def test_ctlReceived_default(self):
        """
        If there's no historian, ctlReceived does nothing by default, or at
        least has no side effects.
        """
        proto = LoggingProtocol()
        proto.ctlReceived('foo')


    def test_ctlReceived_passthru(self):
        """
        Control data can be passed through
        """
        called = []
        
        proto = LoggingProtocol(control=called.append)
        proto.ctlReceived('foo')
        proto.ctlReceived('bar')
        self.assertEqual(called, ['foo', 'bar'])


    def test_outReceived_default(self):
        """
        By default, all output is sent to the historian, marked as "out".
        """
        called = []
        
        proto = LoggingProtocol()
        proto.ctlReceived = called.append
        
        proto.outReceived('foo')
        data = json.loads(called[0])
        self.assertEqual(data['fd'], 1, "File descriptor number should be passed")
        self.assertEqual(data['m'], 'foo', "Message should be passed")
        self.assertEqual(data['lab'], proto.label, "Should send the label")


    def test_outReceived_passthru(self):
        """
        You can ask the protocol for all stdout.
        """
        called = []
        
        proto = LoggingProtocol(stdout=called.append)
        proto.outReceived('foo')
        self.assertEqual(called, ['foo'], "Should have sent stdout")


    def test_errReceived_default(self):
        """
        By default, all stderr is sent to the historian, marked as "err".
        """
        called = []
        
        proto = LoggingProtocol()
        proto.ctlReceived = called.append
        
        proto.errReceived('foo')
        data = json.loads(called[0])
        self.assertEqual(data['fd'], 2, "File descriptor number should be passed")
        self.assertEqual(data['m'], 'foo', "Message should be passed")
        self.assertEqual(data['lab'], proto.label, "Should send the label")


    def test_errReceived_passthru(self):
        """
        You can ask the protocol for all stderr.
        """
        called = []
        
        proto = LoggingProtocol(stderr=called.append)
        proto.errReceived('foo')
        self.assertEqual(called, ['foo'], "Should have sent stderr")


    def test_stdin_on_init(self):
        """
        You can pass a string to be sent on stdin as soon as the protocol is
        connected.
        """
        called = []
        transport = StringTransport()
        transport.closeStdin = lambda: called.append('closeStdin')
        
        proto = LoggingProtocol(stdin='foo')
        proto.makeConnection(transport)
        
        self.assertEqual(transport.value(), 'foo', "Should write to stdin")
        self.assertEqual(called, ['closeStdin'], "Should have closed stdin")


    def test_no_stdin(self):
        """
        If no stdin is given, stdin should not be closed.
        """
        called = []
        transport = StringTransport()
        transport.closeStdin = lambda: called.append('closeStdin')
        
        proto = LoggingProtocol()
        proto.makeConnection(transport)
        
        self.assertEqual(transport.value(), '', "Should not write to stdin")
        self.assertEqual(called, [], "Should not close stdin")



