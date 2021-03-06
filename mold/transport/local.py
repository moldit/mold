from zope.interface import implements
from mold.interface import IConnection

import shlex

from twisted.internet import reactor, defer
from twisted.protocols.ftp import FileConsumer



class LocalConnection(object):
    """
    XXX
    """

    implements(IConnection)


    def close(self):
        return defer.succeed(None)


    def spawnProcess(self, protocol, command):
        """
        Spawn a process
        """
        args = shlex.split(command)
        executable = args[0]
        reactor.spawnProcess(protocol, executable, args, usePTY=True)


    def copyFile(self, path, producer):
        """
        Copy a file to this machine.
        """
        fh = open(path, 'wb', 0)
        #from StringIO import StringIO
        #fh = StringIO()
        consumer = FileConsumer(fh)
        consumer.registerProducer(producer, True)
        return producer.startProducing(consumer)
