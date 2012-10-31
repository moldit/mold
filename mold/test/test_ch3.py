from twisted.trial.unittest import TestCase


from mold.ch3 import fd, decode, encode



class fdTest(TestCase):


    def test_basic(self):
        """
        A stream accepts a name, a file descriptor and some data.
        """
        m = fd('joe', 2, 'data')
        self.assertEqual(m, encode(('joe', 2, {'line': 'data'})))


    def test_binary(self):
        """
        If there's binary data, encode it.
        """
        m = fd('joe', 2, '\x00\x01\xff')
        self.assertEqual(m, encode(('joe', 2, {
            'line': '\x00\x01\xff'.encode('base64'),
            'encoding': 'base64',
        })))



class encode_decodeTest(TestCase):


    def test_works(self):
        """
        You can encode and decode things
        """
        r = decode(encode(['foo', 'bar']))
        self.assertEqual(r, ['foo', 'bar'])



