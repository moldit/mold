from twisted.trial.unittest import TestCase, SkipTest
from twisted.test.proto_helpers import StringTransport
from twisted.internet import reactor, defer, error, interfaces, protocol
from twisted.python.filepath import FilePath
from twisted.python import failure, log
from twisted.python.runtime import platform

from zope.interface.verify import verifyClass, verifyObject
from mock import MagicMock, Mock

import os

from mold.process import (Channel3Protocol, _spawnDefaultArgs, spawnChannel3,
                          SimpleProtocol)
from mold import ch3



class SimpleProtocolTest(TestCase):


    timeout = 1


    def test_init(self):
        """
        Initialize it with a chunk of stdin.
        """
        p = SimpleProtocol('foo')
        t = StringTransport()            
        t.closeStdin = Mock()
        p.makeConnection(t)
        self.assertEqual(t.value(), 'foo')
        self.assertTrue(t.closeStdin.called)


    def test_stdout_err(self):
        """
        You can get stdout and stderr.
        """
        p = SimpleProtocol('foo')
        
        p.childDataReceived(1, 'foo')
        p.childDataReceived(2, 'bar')
        self.assertEqual(p.stdout, 'foo')
        self.assertEqual(p.stderr, 'bar')

        p.childDataReceived(1, 'another foo')
        p.childDataReceived(2, 'another bar')        
        self.assertEqual(p.stdout, 'fooanother foo')
        self.assertEqual(p.stderr, 'baranother bar')


    def test_done(self):
        """
        When the process exits successfully, it's a callback rather than an
        errback
        """
        p = SimpleProtocol('foo')
        p.processEnded(failure.Failure(error.ProcessDone('foo')))
        def check(res):
            self.assertEqual(res, p)
        return p.done.addCallback(check)


    def test_done_error(self):
        """
        If the process exits with an error code, that's an error.
        """
        p = SimpleProtocol('foo')
        p.processEnded(failure.Failure(error.ProcessTerminated(12, 'kill')))
        def eb(res):
            pass
        def cb(res):
            self.fail('should have been an error')
        return p.done.addCallbacks(cb, eb)


class Channel3ProtocolTest(TestCase):


    timeout = 1


    def test_init(self):
        """
        Should take a function that will be called with each piece of channel3
        information and the protocol that will actually handle the data
        """
        data = []
        other_proto = object()
        p = Channel3Protocol('name', data.append, other_proto)
        self.assertEqual(p.name, 'name')
        self.assertEqual(p.sub_proto, other_proto)


    def test_stdout(self):
        """
        When stdout is received, it should be sent to the channel3 receiver
        """
        data = []
        proto = MagicMock()
        p = Channel3Protocol('joe', data.append, proto)
        p.childDataReceived(1, 'some data')
        self.assertEqual(data[0], ch3.fd('joe', 1, 'some data'))
        proto.childDataReceived.assert_called_with(1, 'some data')


    def test_stderr(self):
        """
        When stderr is received, it should be sent to the channel3 receiver.
        """
        data = []
        proto = MagicMock()
        p = Channel3Protocol('joe', data.append, proto)
        p.childDataReceived(2, 'some data')
        self.assertEqual(data[0], ch3.fd('joe', 2, 'some data'))
        proto.childDataReceived.assert_called_with(2, 'some data')


    def test_ch3(self):
        """
        If ch3 data is received, preppend my name to the list and send it on
        again.
        """
        data = []
        proto = MagicMock()
        p = Channel3Protocol('joe', data.append, proto)
        info = ch3.encode(ch3.fd('jim', 2, 'foo bar'))
        p.childDataReceived(3, '%d:%s,' % (len(info), info))
        self.assertEqual(data[0], ch3.fd('joe.jim', 2, 'foo bar'))
        proto.childDataReceived.assert_called_with(3, '%d:%s,' % (len(info), info))


    def test_processEnded(self):
        """
        When the process ends, record the exit information
        """
        data = []
        proto = MagicMock()
        p = Channel3Protocol('joe', data.append, proto)
        self.assertFalse(p.done.called, "Should not have finished yet") 
        
        res = failure.Failure(error.ProcessDone('foo'))
        p.processEnded(res)
        proto.processEnded.assert_called_with(res)
        
        self.assertEqual(data[0], ch3.exit('joe', 0, None))
        self.assertEqual(p.done.result, res)
        return p.done.addErrback(lambda x:None)


    def test_processEnded_signal(self):
        """
        If a process exits with a signal
        """
        data = []        
        p = Channel3Protocol('joe', data.append, MagicMock())
        p.processEnded(failure.Failure(error.ProcessTerminated(12, 'kill')))
        self.assertEqual(data[0], ch3.exit('joe', 12, 'kill'))
        return p.done.addErrback(lambda x:None)


    def test_processExited(self):
        """
        Should call through to sub_proto
        """
        proto = MagicMock()
        p = Channel3Protocol('joe', None, proto)
        p.processExited('whatever')
        proto.processExited.assert_called_with('whatever')


    def test_connectionMade(self):
        """
        Should let you know when the connection is made and inform the sub_proto
        """
        p = Channel3Protocol('joe', None, MagicMock())
        p.connectionMade()
        p.sub_proto.makeConnection.assert_called_with(p)
        def check(r):
            self.assertEqual(r, p)
        return p.started.addCallback(check)


    def test_inConnectionLost(self):
        """
        Should pass through to sub_proto
        """
        proto = MagicMock()
        p = Channel3Protocol('joe', None, proto)
        p.inConnectionLost()
        proto.inConnectionLost.assert_called_with()


    def test_outConnectionLost(self):
        """
        Should pass through to sub_proto
        """
        proto = MagicMock()
        p = Channel3Protocol('joe', None, proto)
        p.outConnectionLost()
        proto.outConnectionLost.assert_called_with()


    def test_errConnectionLost(self):
        """
        Should pass through to sub_proto
        """
        proto = MagicMock()
        p = Channel3Protocol('joe', None, proto)
        p.errConnectionLost()
        proto.errConnectionLost.assert_called_with()


    # IProcessTransport

    def test_IProcessTransport(self):
        """
        The protocol itself should be useable as a transport for some other
        protocol.
        """
        verifyObject(interfaces.IProcessTransport,
                     Channel3Protocol('name', None, None))


    def assertCallTransport(self, name, *args, **kwargs):
        """
        Assert that the method was called on the transport as is and that the
        return result was returned as well
        """
        transport = MagicMock()
        mock = Mock(return_value='foo')
        setattr(transport, name, mock)
        
        proto = Channel3Protocol('name', lambda x:None, MagicMock())
        proto.makeConnection(transport)
        
        result = getattr(proto, name)(*args, **kwargs)
        try:
            mock.assert_called_once_with(*args, **kwargs)
        except AssertionError as e:
            raise AssertionError(str(e), name)
        self.assertEqual(result, 'foo', "Should return the result of "
                                        "transport.%s" % name)


    def test_pid(self):
        """
        Should have the same pid as the transport.
        """
        p = Channel3Protocol('joe', None, MagicMock())
        self.assertEqual(p.pid, None)
        t = StringTransport()
        t.pid = 23
        p.makeConnection(t)
        self.assertEqual(p.pid, 23)


    def test_closeStdin(self):
        self.assertCallTransport('closeStdin')


    def test_closeStdout(self):
        self.assertCallTransport('closeStdout')


    def test_closeStderr(self):
        self.assertCallTransport('closeStderr')


    def test_closeChildFD(self):
        self.assertCallTransport('closeChildFD', 1)


    def test_loseConnection(self):
        self.assertCallTransport('loseConnection')


    def test_signalProcess(self):
        self.assertCallTransport('signalProcess', 'foo')


    def test_getPeer(self):
        self.assertCallTransport('getPeer')


    def test_getHost(self):
        self.assertCallTransport('getHost')


    def test_write(self):
        """
        Writing to stdin should be logged and written
        """
        self.assertCallTransport('write', 'foo bar')
        
        data = []
        t = StringTransport()
        p = Channel3Protocol('joe', data.append, MagicMock())
        p.makeConnection(t)
        p.write('foo bar')
        self.assertEqual(data[0], ch3.fd('joe', 0, 'foo bar'))
        self.assertEqual(t.value(), 'foo bar')


    def test_writeToChild(self):
        """
        Writing to some other channel should be logged and written
        """
        self.assertCallTransport('writeToChild', 22, 'some data')
        
        data = []
        t = MagicMock()
        p = Channel3Protocol('joe', data.append, MagicMock())
        p.makeConnection(t)
        p.writeToChild(22, "some data")
        self.assertEqual(data[0], ch3.fd('joe', 22, 'some data'))


    def test_writeSequence(self):
        """
        Should log and call through
        """
        self.assertCallTransport('writeSequence', ['foo', 'bar'])
        
        data = []
        t = MagicMock()
        p = Channel3Protocol('joe', data.append, MagicMock())
        p.makeConnection(t)
        p.writeSequence(['foo', 'bar'])
        self.assertEqual(data[0], ch3.fd('joe', 0, 'foo'))
        self.assertEqual(data[1], ch3.fd('joe', 0, 'bar'))



class _spawnDefaultArgsTest(TestCase):
    """
    http://twistedmatrix.com/documents/current/api/twisted.internet.interfaces.IReactorProcess.spawnProcess.html
    """

    def test_executable(self):
        r = _spawnDefaultArgs('exec')
        self.assertEqual(r['executable'], 'exec')


    def test_args(self):
        """
        default is ()
        """
        r = _spawnDefaultArgs('exec')
        self.assertEqual(r['args'], ())
        
        r = _spawnDefaultArgs('exec', args=['foo', 'bar'])
        self.assertEqual(r['args'], ['foo', 'bar'])


    def test_env_POSIX(self):
        """
        default on POSIX is {} unless it's None, then it's os.environ.
        """
        if platform.isWindows():
            raise SkipTest('POSIX-only test')

        r = _spawnDefaultArgs('exec')
        self.assertEqual(r['env'], {})
        
        r = _spawnDefaultArgs('exec', env=None)
        self.assertEqual(r['env'], os.environ)

        r = _spawnDefaultArgs('exec', env={'foo': 'bar'})
        self.assertEqual(r['env'], {'foo': 'bar'})


    def test_env_Windows(self):
        """
        default on windows is os.environ updated with whatever
        """
        if not platform.isWindows():
            raise SkipTest('Windows-only test')
        
        r = _spawnDefaultArgs('exec')
        self.assertEqual(r['env'], os.environ)
        
        r = _spawnDefaultArgs('exec', env=None)
        self.assertEqual(r['env'], os.environ)
        
        r = _spawnDefaultArgs('exec', env={'foo': 'bar'})
        e = os.environ.copy()
        e.update({'foo': 'bar'})
        self.assertEqual(r['env'], e)


    def test_path(self):
        """
        Should be current dir
        """
        r = _spawnDefaultArgs('exec')
        self.assertEqual(r['path'], os.curdir)
        
        r = _spawnDefaultArgs('exec', path='foo')
        self.assertEqual(r['path'], 'foo')


    def test_uid(self):
        """
        Should be the current user by default
        """
        if platform.isWindows():
            raise SkipTest('Windows-only test')

        r = _spawnDefaultArgs('exec')
        self.assertEqual(r['uid'], os.geteuid())
        
        r = _spawnDefaultArgs('exec', uid='foo')
        self.assertEqual(r['uid'], 'foo')


    def test_gid(self):
        """
        Should be the current user by default
        """
        if platform.isWindows():
            raise SkipTest('Windows-only test')

        r = _spawnDefaultArgs('exec')
        self.assertEqual(r['gid'], os.getegid())
        
        r = _spawnDefaultArgs('exec', gid='foo')
        self.assertEqual(r['gid'], 'foo')


    def test_usePTY(self):
        """
        Default 0
        """
        r = _spawnDefaultArgs('exec')
        self.assertEqual(r['usePTY'], 0)
        
        r = _spawnDefaultArgs('exec', usePTY=True)
        self.assertEqual(r['usePTY'], True)



class spawnChannel3Test(TestCase):


    timeout = 2


    def test_basic(self):
        """
        You can spawn a process
        """
        proto = MagicMock()
        history = []
        p = spawnChannel3('jim', history.append, proto, '/bin/ls', ['ls', '-al'])
        kwargs = _spawnDefaultArgs('/bin/ls', ['ls', '-al'])
        self.assertEqual(history[0], ch3.spawnProcess('jim', **kwargs),
                         "Should indicate the arguments used to spawn")
        def check(status):
            self.assertEqual(status.value.exitCode, 0)
            for x in history:
                log.msg(x)
        return p.done.addErrback(check)
        


