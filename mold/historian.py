


class RawLogHistorian(object):
    """
    I write messages to a file as they are received (to be read again later).
    """
    
    
    def __init__(self, stream):
        """
        @param stream: A file-like object to which log messages will be written.
        """
        self.stream = stream


    def write(self, message):
        self.stream.write('%d:%s,' % (len(message), message))

