from twisted.trial.unittest import TestCase, SkipTest
from twisted.test.proto_helpers import StringTransport
from twisted.internet import reactor, defer, error
from twisted.python.filepath import FilePath
from twisted.python import failure
from twisted.python.runtime import platform

import os

from mold.process import (Channel3Protocol, _spawnDefaultArgs)
from mold import ch3



class Channel3ProtocolTest(TestCase):


    timeout = 1


    def test_init(self):
        """
        Should take a function that will be called with each piece of channel3
        information
        """
        data = []
        p = Channel3Protocol('name', data.append)
        self.assertEqual(p.name, 'name')


    def test_stdout(self):
        """
        When stdout is received, it should be sent to the channel3 receiver
        """
        data = []
        p = Channel3Protocol('joe', data.append)
        p.childDataReceived(1, 'some data')
        self.assertEqual(data[0], ch3.fd('joe', 1, 'some data'))


    def test_stderr(self):
        """
        When stderr is received, it should be sent to the channel3 receiver.
        """
        data = []
        p = Channel3Protocol('joe', data.append)
        p.childDataReceived(2, 'some data')
        self.assertEqual(data[0], ch3.fd('joe', 2, 'some data'))


    def test_write(self):
        """
        Writing to stdin should be logged.
        """
        data = []
        t = StringTransport()
        p = Channel3Protocol('joe', data.append)
        p.makeConnection(t)
        p.write('foo bar')
        self.assertEqual(data[0], ch3.fd('joe', 0, 'foo bar'))
        self.assertEqual(t.value(), 'foo bar')


    def test_ch3(self):
        """
        If ch3 data is received, preppend my name to the list and send it on
        again.
        """
        data = []
        p = Channel3Protocol('joe', data.append)
        info = ch3.encode(ch3.fd('jim', 2, 'foo bar'))
        p.childDataReceived(3, '%d:%s,' % (len(info), info))
        self.assertEqual(data[0], ch3.fd('joe.jim', 2, 'foo bar'))


    def test_processEnded(self):
        """
        When the process ends, record the exit information
        """
        data = []
        p = Channel3Protocol('joe', data.append)
        self.assertFalse(p.done.called, "Should not have finished yet") 
        
        res = failure.Failure(error.ProcessDone('foo'))
        p.processEnded(res)
        self.assertEqual(data[0], ch3.exit('joe', 0, None))
        self.assertEqual(p.done.result, res)
        return p.done.addErrback(lambda x:None)


    def test_processEnded_signal(self):
        """
        If a process exits with a signal
        """
        data = []
        p = Channel3Protocol('joe', data.append)
        p.processEnded(failure.Failure(error.ProcessTerminated(12, 'kill')))
        self.assertEqual(data[0], ch3.exit('joe', 12, 'kill'))
        return p.done.addErrback(lambda x:None)


    def test_connectionMade(self):
        """
        Should let you know when the connection is made
        """
        p = Channel3Protocol('joe', None)
        p.connectionMade()
        def check(r):
            self.assertEqual(r, p)
        return p.started.addCallback(check)



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


