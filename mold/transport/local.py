from zope.interface import implements
from mold.interface import IConnection

import shlex
import re

from twisted.internet import reactor, defer
from twisted.internet.protocol import ProcessProtocol





class LocalConnection(object):
    """
    XXX
    """

    implements(IConnection)


    def spawnProcess(self, protocol, command):
        """
        Spawn a process
        """
        args = shlex.split(command)
        executable = args[0]
        reactor.spawnProcess(protocol, executable, args)