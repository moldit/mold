from twisted.trial.unittest import TestCase


from mold.netstring import NetstringReader, KeyPairReader


class NetstringReaderTest(TestCase):

    def test_wholeString(self):
        """
        A function is called when a netstring is found.
        """
        called = []
        r = NetstringReader(called.append)
        r.dataReceived('1:a,')
        self.assertEqual(called, ['a'])


    def test_multipleAtOnce(self):
        """
        If more than one netstring is received at a time, the receiver should
        be called with all netstrings.
        """
        called = []
        r = NetstringReader(called.append)
        r.dataReceived('1:a,1:b,1:c,')
        self.assertEqual(called, ['a', 'b', 'c'])


    def test_partial(self):
        """
        If a netstring is received a piece at a time, it should still call
        the receiver function when the complete string is received.
        """
        called = []
        r = NetstringReader(called.append)
        r.dataReceived('2:a')
        self.assertEqual(called, [])
        r.dataReceived('a')
        self.assertEqual(called, [])
        r.dataReceived(',2:b')
        self.assertEqual(called, ['aa'])
        r.dataReceived('b,')
        self.assertEqual(called, ['aa', 'bb'])



class KeyPairReaderTest(TestCase):

    def test_pair(self):
        """
        If a pair is given, a function should be called with the pair.
        """
        called = []
        r = KeyPairReader(called.append)
        r.stringReceived('foo')
        r.stringReceived('bar')
        self.assertEqual(called, [('foo', 'bar')])

    def test_multiple(self):
        """
        If multiple pairs are given, they should be all be sent to the
        receiver.
        """
        called = []
        r = KeyPairReader(called.append)
        r.stringReceived('foo')
        r.stringReceived('bar')
        r.stringReceived('hey')
        self.assertEqual(called, [('foo', 'bar')])
        r.stringReceived('ho')
        self.assertEqual(called, [('foo', 'bar'), ('hey', 'ho')])
