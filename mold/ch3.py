

__all__ = ['Message', 'encode', 'decode', 'fd', 'spawnProcess', 'exit']


import os
import json

from collections import namedtuple


decode = json.loads
encode = json.dumps


Message = namedtuple('Message', ['name', 'key', 'data'])



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



def spawnProcess(name, executable, args, env, path, uid, gid, usePTY):
    """
    XXX
    """
    return Message(name, 'spawn', {
        'executable': executable,
        'args': args,
        'env': env,
        'path': path,
        'uid': uid,
        'gid': gid,
        'usePTY': usePTY,
    })



def exit(name, code, signal):
    """
    """
    return Message(name, 'exit', {
        'code': code,
        'signal': signal,
    })


