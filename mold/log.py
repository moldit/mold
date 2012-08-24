
import json



class MessageFactory(object):
    """
    I produce a common set of messages to send to a Historian.
    """

    
    def fd(self, label, fd, data):
        return json.dumps({
            'lab': label,
            'ev': 'fd',
            'fd': fd,
            'm': data,
        })


    def processSpawned(self, label, bin, args, env, path, uid, gid, usePTY):
        return json.dumps({
            'ev': 'pspawn',
            'lab': label,
            'bin': bin,
            'args': args,
            'env': env,
            'path': path,
            'uid': uid,
            'gid': gid,
            'pty': usePTY,
        })


    def processEnded(self, label, exitCode, signal):
        return json.dumps({
            'lab': label,
            'ev': 'pexit',
            'exitCode': exitCode,
            'signal': signal,
        })