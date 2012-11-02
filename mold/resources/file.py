"""
file Resource
"""

from twisted.python import usage
from twisted.python.filepath import FilePath
import sys
import json
import pwd, grp, os


def permsString(perms):
    n = '0'
    for i,thing in enumerate([perms.other, perms.group, perms.user]):
        x = 0
        if thing.read:
            x = 1
        if thing.write:
            x |= 2
        if thing.execute:
            x |= 4
        n += str(x)
    return n



def inspect(doc):
    data = json.loads(doc)
    path = FilePath(data['path'])
    ret = {'kind': 'file', 'path': path.path, 'exists': path.exists()}
    if not ret['exists']:
        return ret
            
    ret['filetype'] = 'dir'
    ret['owner'] = pwd.getpwuid(path.getUserID()).pw_name
    ret['group'] = grp.getgrgid(path.getGroupID()).gr_name
    ret['perms'] = permsString(path.getPermissions())
    ret['ctime'] = int(path.statinfo.st_ctime)
    ret['mtime'] = int(path.statinfo.st_mtime)
    ret['atime'] = int(path.statinfo.st_atime)
    return ret



class Options(usage.Options):


    subCommands = [
        ['inspect', None, usage.Options, "Inspect the state of a file"],
    ]



def main(args=sys.argv[1:], stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr):
    options = Options()
    options.parseOptions(args)

    # XXX all this stdin/out/err faking is just for testing.  Maybe there's
    # a better way to do this.

    if options.subCommand == 'inspect':
        stdout.write(json.dumps(inspect(stdin.read())))
