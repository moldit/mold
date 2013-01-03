from twisted.application import service, internet
from twisted.internet import endpoints, protocol
from twisted.python import usage

from mold.network import simple


class Options(usage.Options):

    longdesc = ''

    subCommands = [
        ('minion', None, simple.MinionOptions, "Start a minion"),
    ]



def makeService(options):
    # See https://bitbucket.org/jerub/twisted-plugin-example/src/2baa0e726917/examplepackage/examplemodule.py?at=default
    print "I don't work yet"
    return simple.makeService(options.subOptions)