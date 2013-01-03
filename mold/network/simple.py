from twisted.protocols import amp
from twisted.internet.protocol import Factory, ClientCreator
from twisted.internet import endpoints, reactor
from twisted.python import usage
from twisted.application import internet, service


class Run(amp.Command):
    arguments = [
        ('name', amp.String()),
        ('args', amp.ListOf(amp.String())),
        ('stdin', amp.String()),
    ]
    response = [
        ('exitcode', amp.Integer()),
        ('stdout', amp.String()),
        ('stderr', amp.String()),
    ]




class Minion(amp.AMP):


    @Run.responder
    def run(self, name, args, stdin):
        r = self.factory.runner.run(name, args, stdin)
        return r.done.addCallback(self.runDone)


    def runDone(self, proto):
        print proto
        print dir(proto)
        return {
            'exitcode': 0,
            'stdout': proto.stdout,
            'stderr': proto.stderr,
        }


def _run(host, port, name, args, stdin):
    return ClientCreator(reactor, amp.AMP).connectTCP(host, port).addCallback(
        lambda p: p.callRemote(Run, name=name, args=args, stdin=stdin)
        )


def runOne(host, port, name, args, stdin):
    def gotResponse(response):
        print response
    return _run(host, port, name, args, stdin).addBoth(gotResponse)


class MinionOptions(usage.Options):

    longdesc = 'Start a minion daemon'
    usage = '[options] minion-root'

    optParameters = [
        ('endpoint', 'e', 'tcp:6030', "Endpoint on which to listen"),
    ]
    
    def parseArgs(self, root):
        self['root'] = root



def makeService(options):
    from mold.process import ScriptRunner
    f = Factory()
    f.protocol = Minion
    called = []
    f.runner = ScriptRunner(options['root'], called.append)
    
    endpoint = endpoints.serverFromString(reactor, options['endpoint'])
    server_service = internet.StreamServerEndpointService(endpoint, f)
    server_service.setName('mold minion')
    
    return server_service