from zope.interface import Interface


class IConnection(Interface):
    """
    A connection to a machine that allows executing processes.
    """
    
    def spawnProcess(protocol, command):
        """
        Spawn a process on the connection.
        
        @param command: A byte string shell command.
        @param processprotocol: A ProcessProtocol instance that will handle
            the input/output of the process.
        """



class IConnectionMaker(Interface):


    def getConnection(uri):
        """
        Get a connection for the given URI.

        @param uri: A URI defining all connection requirements for a server.

        @return: C{Deferred} L{IConnection}
        """



class IPasswordManager(Interface):


    def getPassword(uri):
        """
        Given a connection URI, get the password needed to connect.
        """