"""
Main entry point for `mold` command line tool.
"""

from __future__ import print_function

from twisted.python import usage
from twisted.internet import reactor



class CreateMinionOptions(usage.Options):

    synopsis = 'path'
    
    def parseArgs(self, path):
        self['path'] = path



class Options(usage.Options):

    subCommands = [
        ['create-minion', None, CreateMinionOptions, "Create a minion"],
    ]



def main():
    """
    XXX
    """
    from twisted.internet import reactor
    options = Options()
    options.parseOptions()

    so = options.subOptions
    if options.subCommand == 'create-minion':
        from mold.minion.install import Directory
        d = Directory(so['path'])
        d.install()