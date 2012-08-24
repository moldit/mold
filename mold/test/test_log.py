from twisted.trial.unittest import TestCase


from mold.log import Logger


class MemoryLogger(Logger):

    def __init__(self):
        self.messages = []


    def sendMessage(self, message):
        self.messages.append(message)



class LoggerTest(TestCase):


    def test_sendMessage(self):
        """
        You have to subclass and implement the message sending.
        """
        l = Logger()
        self.assertRaises(NotImplementedError, l.sendMessage, 'foo')


    def test_fd(self):
        """
        You can signal bytes moving over a file descriptor
        """
        l = MemoryLogger()
        l.fd('label', 0, 'hello')
        
        m = l.messages[-1]
        self.assertEqual(m['ev'], 'fd')
        self.assertEqual(m['fd'], 0)
        self.assertEqual(m['lab'], 'label')
        self.assertEqual(m['m'], 'hello')


    def test_processEnded(self):
        """
        You can signal that a process ended
        """
        l = MemoryLogger()
        l.processEnded('label', 1, 2)
        
        m = l.messages[-1]
        self.assertEqual(m['ev'], 'pexit')
        self.assertEqual(m['lab'], 'label')
        self.assertEqual(m['exitCode'], 1)
        self.assertEqual(m['signal'], 2)

