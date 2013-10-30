from twisted.trial.unittest import TestCase

from zope.interface.verify import verifyObject

from mold.transport.test.mixin import FunctionalConnectionTestMixin
from mold.interface import IConnection
from mold.transport.local import LocalConnection



class LocalFunctionalTest(FunctionalConnectionTestMixin, TestCase):


    def getConnection(self):
        return LocalConnection()



class LocalConnectionTest(TestCase):


    def test_IConnection(self):
        verifyObject(IConnection, LocalConnection())
