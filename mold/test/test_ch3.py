from twisted.trial.unittest import TestCase
import json


from mold.ch3 import fd



class fdTest(TestCase):


    def test_basic(self):
        """
        A stream accepts a name, a file descriptor and some data.
        """
        m = fd('joe', 2, 'data')
        self.assertEqual(m, json.dumps(('joe', 2, {'line': 'data'})))


    def test_binary(self):
        """
        If there's binary data, encode it.
        """
        m = fd('joe', 2, '\x00\x01\xff')
        self.assertEqual(m, json.dumps(('joe', 2, {
            'line': '\x00\x01\xff'.encode('base64'),
            'encoding': 'base64',
        })))