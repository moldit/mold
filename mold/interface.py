from zope.interface import Interface


class IConnection(Interface):


    def executeProcess(protocol, bin, args, env, path, uid, gid):
        """
        Execute a process.

        @type protocol: C{ProcessProtocol}
        """


    def sendStream(path, stream):
        """
        Send a file over this connection.
        """


    def hashFile(path):
        """
        Get the hash of a remote file.
        """


    def disconnected():
        """
        Get a Deferred which will fire when this connection has been
        disconnected.
        """



class IConnectionMaker(Interface):


    def getConnection(uri):
        """
        Get a connection for the given URI.
        """



class IPasswordManager(Interface):


    def getPassword(uri, translated_uri):
        """
        Given a connection URI, get the password needed to connect.
        """