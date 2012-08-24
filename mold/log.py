


class Logger(object):
    """
    I provide a common set of messages to send to a Historian.
    """
    
    def sendMessage(self, message):
        """
        Send a message along... whatever that means for you.
        
        @type message: dict
        @param message: Dictionary of data to send along.
        """
        raise NotImplementedError()
    
    
    def fd(self, label, fd, data):
        self.sendMessage({
            'lab': label,
            'ev': 'fd',
            'fd': fd,
            'm': data,
        })


    def processEnded(self, label, exitCode, signal):
        self.sendMessage({
            'lab': label,
            'ev': 'pexit',
            'exitCode': exitCode,
            'signal': signal,
        })