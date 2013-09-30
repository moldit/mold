from twisted.trial.unittest import TestCase
from twisted.internet import reactor
from twisted.internet.endpoints import UNIXClientEndpoint
from twisted.python.filepath import FilePath

from zope.interface.verify import verifyObject

import getpass

from mold.interface import IConnection, IConnectionMaker
from mold.transport.ssh import SSHConnection, SSHConnectionMaker, parseURI
from mold.transport.ssh import connectionParamsFromEnv



class SSHConnectionTest(TestCase):


    def test_IConnection(self):
        verifyObject(IConnection, SSHConnection())



class SSHConnectionMakerTest(TestCase):


    def test_IConnectionMaker(self):
        verifyObject(IConnectionMaker, SSHConnectionMaker())


    def test_getConnection(self):
        maker = SSHConnectionMaker()




class parseURITest(TestCase):


    def test_basic(self):
        """
        A basic SSH URI should be parseable into a dictionary of things.
        """
        r = parseURI('ssh://joe@10.1.2.3:2903')
        self.assertEqual(r['username'], 'joe')
        self.assertEqual(r['hostname'], '10.1.2.3')
        self.assertEqual(r['port'], 2903)



class connectionParamsFromEnvTest(TestCase):


    def test_defaults(self):
        """
        If the environment is empty, these are the defaults.
        """
        p = connectionParamsFromEnv({}, reactor)
        self.assertEqual(p['username'], getpass.getuser(), "Should default "
                         "to the current user")
        self.assertEqual(p['port'], 22)
        self.assertEqual(p['agentEndpoint'], None)
        self.assertEqual(p['knownHosts'], None)


    def test_agentEndpoint(self):
        """
        If SSH_AUTH_SOCK is defined, use that for the agentEndpoint
        """
        p = connectionParamsFromEnv({
            'SSH_AUTH_SOCK': '/tmp/foo',
        }, reactor)
        self.assertNotEqual(p['agentEndpoint'], None)
        self.assertTrue(isinstance(p['agentEndpoint'], UNIXClientEndpoint))
        self.assertEqual(p['agentEndpoint']._reactor, reactor)
        self.assertEqual(p['agentEndpoint']._path, '/tmp/foo')

