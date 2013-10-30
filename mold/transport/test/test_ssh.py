from twisted.trial.unittest import TestCase, SkipTest
from twisted.internet import defer

from zope.interface.verify import verifyObject

from mock import MagicMock, create_autospec

import os

from mold.interface import IConnection, IConnectionMaker
from mold.transport.test.mixin import FunctionalConnectionTestMixin
from mold.transport.ssh import SSHConnection, SSHConnectionMaker, parseURI
from mold.transport.ssh import AuthenticationLacking


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


    def test_noPassword_noIdentity_noPasswordPrompt(self):
        """
        If a uri without a password or an identity is supplied, AND there's no
        password prompting function, fail before contacting the server, unless
        that is overridden.
        """
        maker = SSHConnectionMaker(askForPassword=None)
        self.assertFailure(maker.getConnection('ssh://foo@127.0.0.1'),
                           AuthenticationLacking)


    @defer.inlineCallbacks
    def test_noPassword_noIdentity_passwordPrompt(self):
        """
        If a uri lacking a password AND an identity is supplied, but there's
        an askForPassword function, call the askForPassword function to get
        the password.
        """
        prompter = MagicMock(return_value=defer.succeed('passWord'))
        maker = SSHConnectionMaker(askForPassword=prompter)
        maker._connect = create_autospec(maker._connect,
                                         return_value=defer.succeed('res'))

        result = yield maker.getConnection('ssh://foo@127.0.0.1')

        self.assertEqual(prompter.call_count, 1, "Should have asked for the "
                         "password")
        self.assertEqual(maker._connect.call_count, 1, "Should have called "
                         "_connect")
        kwargs = maker._connect.call_args[0][0]
        self.assertEqual(kwargs['username'], 'foo')
        self.assertEqual(kwargs['password'], 'passWord')
        self.assertEqual(kwargs['hostname'], '127.0.0.1')
        self.assertEqual(kwargs['port'], 22)
        self.assertEqual(result, 'res')



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
