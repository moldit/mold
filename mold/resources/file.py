"""
file Resource
"""

from twisted.python import usage
from twisted.python.filepath import FilePath
import sys
import json


def inspect(doc):
    data = json.loads(doc)
    path = FilePath(data['path'])
    return json.dumps({
        'kind': 'file',
        'path': path.path,
        'exists': path.exists(),
    })



class Options(usage.Options):


    subCommands = [
        ['inspect', None, usage.Options, "Inspect the state of a file"],
    ]



def main(args=sys.argv[1:], stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr):
    options = Options()
    options.parseOptions(args)

    # XXX all this stdin/out/err faking is just for testing.  Maybe there's
    # a better way to do this.
    real_stdin = sys.stdin
    real_stdout = sys.stdout
    real_stderr = sys.stderr
    def restore():
        sys.stdin = real_stdin
        sys.stdout = real_stdout
        sys.stderr = real_stderr
        
    try:
        sys.stdin = stdin
        sys.stdout = stdout
        sys.stderr = stderr
        if options.subCommand == 'inspect':
            stdout.write(inspect(stdin.read()))
    except:
        restore()
        raise
    else:
        restore()
