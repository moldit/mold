from twisted.trial.unittest import TestCase
from twisted.internet import reactor
from twisted.internet.endpoints import UNIXClientEndpoint

from zope.interface.verify import verifyObject

import getpass
import os

from mold.transport.test.mixin import FunctionalConnectionTestMixin

from mold.interface import IConnection, IConnectionMaker
from mold.transport.ssh import SSHConnection, SSHConnectionMaker, parseURI

_ssh_test_uri_varname = 'MOLD_TEST_SSH_URI'
_skip_functional_test = 'Provide an SSH endpoint as %r to run this test' % (
                        _ssh_test_uri_varname)
SSH_TEST_URI = os.environ.get(_ssh_test_uri_varname)
if SSH_TEST_URI:
    _skip_functional_test = None




class SSHFunctionalTest(FunctionalConnectionTestMixin, TestCase):


    skip = _skip_functional_test
    

    def getConnection(self):
        pass



class SSHConnectionTest(TestCase):


    def test_IConnection(self):
        verifyObject(IConnection, SSHConnection())



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
        self.assertEqual(r['port'], 2903)
