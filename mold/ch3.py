
import os
import json

from collections import namedtuple


decode = json.loads
encode = json.dumps


Message = namedtuple('Message', ['name', 'key', 'data'])

undef = object()


def fd(name, fdnumber, data):
    """
    XXX
    """
    r = {'line': data}
    try:
        encode(r)
    except UnicodeDecodeError as e:
        r['line'] = data.encode('base64')
        r['encoding'] = 'base64'    
    return Message(name, fdnumber, r)



def spawnProcess(name, executable, args=None, env=undef, path=None, uid=None, 
                 gid=None):
    """
    XXX
    """
    if env is undef:
        env = {}
    elif env is None:
        env = dict(os.environ)
    path = path or os.curdir
    return Message(name, 'spawn', {
        'executable': executable,
        'args': args,
        'env': env,
        'path': path,
        'uid': uid,
        'gid': gid,
    })



def exit(name, code, signal):
    """
    """
    return Message(name, 'exit', {
        'code': code,
        'signal': signal,
    })


