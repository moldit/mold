from twisted.trial.unittest import TestCase
from twisted.internet import defer
from twisted.python.filepath import FilePath
from twisted.python import log

import json
import pwd
import grp
import os

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
        root.chmod(0777)
        
        stdout, stderr, code = self.runScript(['inspect'], json.dumps({
            'kind': 'file',
            'path': root.path,
        }))
        data = json.loads(stdout)
        self.assertEqual(data['kind'], 'file')
        self.assertEqual(data['path'], root.path)
        self.assertEqual(data['exists'], True)
        self.assertEqual(data['filetype'], 'dir')
        self.assertEqual(data['owner'], pwd.getpwuid(os.geteuid()).pw_name)
        self.assertEqual(data['group'], grp.getgrgid(os.getegid()).gr_name)
        self.assertEqual(data['perms'], '0777')
        root.restat()
        self.assertEqual(data['ctime'], int(root.statinfo.st_ctime))
        self.assertEqual(type(data['ctime']), int)
        self.assertEqual(data['mtime'], int(root.statinfo.st_mtime))
        self.assertEqual(type(data['mtime']), int)
        self.assertEqual(data['atime'], int(root.statinfo.st_atime))
        self.assertEqual(type(data['atime']), int)
