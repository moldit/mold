from twisted.trial.unittest import TestCase

import os

from mold.ch3 import (fd, spawnProcess, exit, decode, encode, Message)



class MessageTest(TestCase):


    def test_attrs(self):
        """
        Every message has these attributes
        """
        m = Message('name', 'key', 'data')
        self.assertEqual(m.name, 'name')
        self.assertEqual(m.key, 'key')
        self.assertEqual(m.data, 'data')


    def test_equality(self):
        """
        Equal messages are equal
        """
        m = Message('name', 'key', 'data')
        m2 = Message('name', 'key', 'data')
        self.assertEqual(m, m2)



class exitTest(TestCase):


    def test_basic(self):
        """
        It takes an exit code and signal
        """
        self.assertEqual(exit('joe', 3, 'signal'),
                         Message('joe', 'exit', {
                            'code': 3,
                            'signal': 'signal',
                         }))



class spawnProcessTest(TestCase):


    def test_basic(self):
        """
        You can indicate that a process was spawned
        """
        self.assertEqual(spawnProcess('joe', 'executable',
                         args=['foo', 'bar'],
                         env={'something': 'here'},
                         path='some path',
                         uid='userid',
                         gid='groupid'),
                         Message('joe', 'spawn', {
                            'executable': 'executable',
                            'args': ['foo', 'bar'],
                            'env': {'something': 'here'},
                            'path': 'some path',
                            'uid': 'userid',
                            'gid': 'groupid',
                        })
        )


    def test_noEnv(self):
        """
        If no environment is given, it's as if an empty environment was given
        (for POSIX only.)  See
        U{http://twistedmatrix.com/documents/current/api/twisted.internet.interfaces.IReactorProcess.spawnProcess.html}
        for env behavior.
        """
        self.assertEqual(spawnProcess('joe', 'executable'),
                         spawnProcess('joe', 'executable', env={}))


    def test_env_None(self):
        """
        If env is None, pass os.environ on POSIX and Windows
        """
        self.assertEqual(spawnProcess('joe', 'executable', env=None),
                         spawnProcess('joe', 'executable', env=dict(os.environ)))


    def test_path_none(self):
        """
        If path isn't set, use the current directory
        """
        self.assertEqual(spawnProcess('joe', 'exec'),
                         spawnProcess('joe', 'exec', path=os.curdir))


class fdTest(TestCase):


    def test_basic(self):
        """
        A stream accepts a name, a file descriptor and some data.
        """
        m = fd('joe', 2, 'data')
        self.assertEqual(m, Message('joe', 2, {'line': 'data'}))


    def test_binary(self):
        """
        If there's binary data, encode it.
        """
        m = fd('joe', 2, '\x00\x01\xff')
        self.assertEqual(m, Message('joe', 2, {
            'line': '\x00\x01\xff'.encode('base64'),
            'encoding': 'base64',
        }))



class encode_decodeTest(TestCase):


    def test_works(self):
        """
        You can encode and decode things
        """
        r = decode(encode(['foo', 'bar']))
        self.assertEqual(r, ['foo', 'bar'])



