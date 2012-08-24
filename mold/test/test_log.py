from twisted.trial.unittest import TestCase

import json


from mold.log import MessageFactory



class MessageFactoryTest(TestCase):


    def test_fd(self):
        """
        You can signal bytes moving over a file descriptor
        """
        f = MessageFactory()
        m = json.loads(f.fd('label', 0, 'hello'))
        
        self.assertEqual(m['ev'], 'fd')
        self.assertEqual(m['fd'], 0)
        self.assertEqual(m['lab'], 'label')
        self.assertEqual(m['m'], 'hello')


    def test_processEnded(self):
        """
        You can signal that a process ended
        """
        f = MessageFactory()
        m = json.loads(f.processEnded('label', 1, 2))

        self.assertEqual(m['ev'], 'pexit')
        self.assertEqual(m['lab'], 'label')
        self.assertEqual(m['exitCode'], 1)
        self.assertEqual(m['signal'], 2)

