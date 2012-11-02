from twisted.trial.unittest import TestCase
from twisted.internet import defer
from twisted.python.filepath import FilePath
from twisted.python import log

import json

from StringIO import StringIO



class file_inspect_Test(TestCase):


    def runScript(self, args, stdin):
        """
        Run the script (or at least pretend to)
        
        @return: A tuple of (stdout, stderr, exitcode)
        """
        from mold.resources.file import main
        stdin = StringIO(stdin)
        stdout = StringIO()
        stderr = StringIO()
        code = main(args, stdin, stdout, stderr)
        return (stdout.getvalue(), stderr.getvalue(), code)
        

    def test_dne(self):
        """
        A file that doesn't exist should say so.
        """
        root = FilePath(self.mktemp())
        stdout, stderr, code = self.runScript(['inspect'], json.dumps({
            'kind': 'file',
            'path': root.path,
        }))
        data = json.loads(stdout)
        self.assertEqual(data, {
            'kind': 'file',
            'path': root.path,
            'exists': False,
        })


    def test_directory(self):
        """
        A directory can exist
        """
        root = FilePath(self.mktemp())
        root.makedirs()
        
        stdout, stderr, code = self.runScript(['inspect'], json.dumps({
            'kind': 'file',
            'path': root.path,
        }))
        data = json.loads(stdout)
        self.assertEqual(data, {
            'kind': 'file',
            'path': root.path,
            'exists': True,
        })
