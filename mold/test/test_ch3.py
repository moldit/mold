from twisted.trial.unittest import TestCase
from zope.interface.verify import verifyObject

import os

from mold.ch3 import ProcessStream, ProcessStarted, ProcessEnded



class ProcessStreamTest(TestCase):


    def test_init(self):
        """
        You can initialize it with pid, descriptor and data
        """
        d = ProcessStream(12343, 0, 'data')
        self.assertEqual(d.pid, 12343)
        self.assertEqual(d.fd, 0)
        self.assertEqual(d.data, 'data')



class ProcessStartedTest(TestCase):


    def test_init(self):
        """
        You can initialize with all the args a spawned process will have
        """
        d = ProcessStarted(562, 123, 'executable', args=['foo', 'bar'],
                         env={'something': 'here'},
                         path='some path',
                         uid='userid',
                         gid='groupid',
                         usePTY='foo')
        self.assertEqual(d.ppid, 562)
        self.assertEqual(d.pid, 123)
        self.assertEqual(d.executable, 'executable')
        self.assertEqual(d.args, ['foo', 'bar'])
        self.assertEqual(d.env, {'something': 'here'})
        self.assertEqual(d.path, 'some path')
        self.assertEqual(d.uid, 'userid')
        self.assertEqual(d.gid, 'groupid')
        self.assertEqual(d.usePTY, 'foo')



class ProcessEndedTest(TestCase):


    def test_init(self):
        """
        You can initialize with the right stuff to indicate a process exit
        """
        d = ProcessEnded(123, 20, 'signal')
        self.assertEqual(d.pid, 123)
        self.assertEqual(d.exitcode, 20)
        self.assertEqual(d.signal, 'signal')
