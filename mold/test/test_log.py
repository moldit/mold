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


    def test_processSpawned(self):
        """
        You can signal that a process was started.
        """
        f = MessageFactory()
        m = json.loads(f.processSpawned('label', 'bin', ['arg1', 'arg2'],
                                        {'env1': 'foo'}, 'path',
                                        'user1', 'group1', False))
        
        self.assertEqual(m['ev'], 'pspawn')
        self.assertEqual(m['lab'], 'label')
        self.assertEqual(m['bin'], 'bin')
        self.assertEqual(m['args'], ['arg1', 'arg2'])
        self.assertEqual(m['env'], {'env1': 'foo'})
        self.assertEqual(m['path'], 'path')
        self.assertEqual(m['uid'], 'user1')
        self.assertEqual(m['gid'], 'group1')
        self.assertEqual(m['pty'], False)


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

