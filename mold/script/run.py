from twisted.python import usage


class Options(usage.Options):

    longdesc = "Execute a process on remote machines."

    def parseArgs(self, *args):
        print args


def main(options, main_options=None):
    print 'executing'