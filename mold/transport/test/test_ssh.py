from twisted.trial.unittest import TestCase

from zope.interface.verify import verifyObject

import os

from mold.interface import IConnection, IConnectionMaker
from mold.transport.test.mixin import FunctionalConnectionTestMixin
from mold.transport.ssh import SSHConnection, SSHConnectionMaker, parseURI


_ssh_test_uri_varname = 'MOLD_TEST_SSH_URI'
_skip_functional_test = 'Provide an SSH endpoint as %r to run this test' % (
                        _ssh_test_uri_varname)
SSH_TEST_URI = os.environ.get(_ssh_test_uri_varname)
if SSH_TEST_URI:
    _skip_functional_test = None




class SSHFunctionalFromMixinTest(FunctionalConnectionTestMixin, TestCase):


    skip = _skip_functional_test
    

    def getConnection(self):
        maker = SSHConnectionMaker()
        return maker.getConnection(SSH_TEST_URI)


class SSHConnectionTest(TestCase):


    def test_IConnection(self):
        verifyObject(IConnection, SSHConnection(None))



class SSHConnectionMakerTest(TestCase):


    def test_IConnectionMaker(self):
        verifyObject(IConnectionMaker, SSHConnectionMaker())



class parseURITest(TestCase):


    def test_basic(self):
        """
        A basic SSH URI should be parseable into a dictionary of things.
        """
        r = parseURI('ssh://joe@10.1.2.3:2903')
        self.assertEqual(r['username'], 'joe')
        self.assertEqual(r['hostname'], '10.1.2.3')
        self.assertEqual(r['password'], None)
        self.assertEqual(r['port'], 2903)


    def test_password(self):
        """
        A password can be included.
        """
        r = parseURI('ssh://joe:foo@10.1.2.3')
        self.assertEqual(r['password'], 'foo')


    def test_special_chars(self):
        """
        Special characters should be handled
        """
        r = parseURI('ssh://%21:%40@10.1.2.3')
        self.assertEqual(r['username'], '!')
        self.assertEqual(r['password'], '@')
