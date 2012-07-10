from twisted.trial.unittest import TestCase
from zope.interface.verify import verifyClass
from StringIO import StringIO

import json

from mold.interface import ILogger
from mold.logger import FileLogger



class FileLoggerTest(TestCase):


    def test_ILogger(self):
        verifyClass(ILogger, FileLogger)



    def test_msg(self):
        """
        You can log a string to the FileLogger
        """
        files = []
        def fileFactory():
            files.append(StringIO())
            return files[-1]
        fl = FileLogger()
        fl.fileFactory = fileFactory

        fl.msg('foo')
        fl.msg('bar')
        fh = files[-1]
        self.assertEqual(fh.getvalue(), "foo\nbar\n", "Should have logged "
                         "the data")


    def test_msg_multichannel(self):
        """
        You can log to multiple channels
        """
        files = []
        def fileFactory():
            files.append(StringIO())
            return files[-1]
        fl = FileLogger()
        fl.fileFactory = fileFactory

        fl.msg('foo', 'channel1')
        fl.msg('bar', 'channel2')
        fh1 = files[-2]
        fh2 = files[-1]
        self.assertEqual(fh1.getvalue(), "foo\n")
        self.assertEqual(fh2.getvalue(), "bar\n")


    def test_msg_error(self):
        """
        If there's an error (unicode or otherwise), do something.
        """
        self.fail('write me')


    def test_json(self):
        """
        You can log json-able data
        """
        files = []
        def fileFactory():
            files.append(StringIO())
            return files[-1]
        fl = FileLogger()
        fl.fileFactory = fileFactory

        fl.json('foo')
        fl.json({'foo': 'bar'})
        fh = files[-1]
        expected = '%s\n%s\n' % (json.dumps('foo'), json.dumps({'foo': 'bar'}))
        self.assertEqual(fh.getvalue(), expected, "Should have logged the data")


    def test_json_notjson(self):
        """
        Trying to log things that can't be json is bad
        """
        self.fail('write me')
