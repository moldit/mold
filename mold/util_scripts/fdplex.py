#!/usr/bin/python
# spawn a processcombine stdin with channel 3 and write it to stdout as netstrings

import sys
import os
import pty
import subprocess

master, slave = pty.openpty()
p = subprocess.Popen(sys.argv[1:], stdin=slave, stdout=slave, stderr=slave,
                     close_fds=True)
out, err = p.communicate()

#sys.stdout.write('3:fd1,%d:%s,' % (len(out), out))
#sys.stdout.write('3:fd2,%d:%s,' % (len(err), err))
rc = str(p.returncode)

sys.stdout.write('2:rc,%d:%s,' % (len(rc), rc))
sys.exit(p.returncode)