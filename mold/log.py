


class MessageFactory(object):
    """
    I produce a common set of messages to send to a Historian.
    """

    
    def fd(self, label, fd, data):
        return {
            'lab': label,
            'ev': 'fd',
            'fd': fd,
            'm': data,
        }


    def processEnded(self, label, exitCode, signal):
        return {
            'lab': label,
            'ev': 'pexit',
            'exitCode': exitCode,
            'signal': signal,
        }