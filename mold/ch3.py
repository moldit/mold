
import os
import json


decode = json.loads
encode = json.dumps

undef = object()


def fd(name, fdnumber, data):
    """
    XXX
    """
    try:
        return encode((name, fdnumber, {'line': data}))
    except UnicodeDecodeError as e:
        return encode((name, fdnumber, {
            'line': data.encode('base64'),
            'encoding': 'base64',
        }))



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
    return encode((name, 'spawn', {
        'executable': executable,
        'args': args,
        'env': env,
        'path': path,
        'uid': uid,
        'gid': gid,
    }))



def exitCode(name, code):
    return encode((name, 'exitcode', code))