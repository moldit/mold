from twisted.trial.unittest import TestCase

import json

from mold.process import LoggingProtocol



class LoggingProtocolTest(TestCase):


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


    def test_ctlReceived_historian(self):
        """
        If the LoggingProtocol has a historian, then ctlReceived will send all
        data to it.
        """
        called = []
        
        proto = LoggingProtocol(historian=called.append)
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