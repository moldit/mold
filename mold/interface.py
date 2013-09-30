from zope.interface import Interface


class IProcessRunner(Interface):


    def executeProcess(protocol, bin, args, env, path, uid, gid):
        """
        Execute a process.

        @type protocol: C{ProcessProtocol}
        """

