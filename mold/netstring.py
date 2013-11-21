class NetstringReader(object):
    """
    I read netstrings.
    """

    def __init__(self, receiver):
        """
        @param receiver: Function to be called each time I find a netstring.
        """
        self.receiver = receiver
        self._buf = ''


    def dataReceived(self, data):
        """
        Read some more netstring data.

        @param data: Some bytes probably in the netstring format.
        """
        # XXX dirty implementation for now.  Optimize for speed later.
        # XXX also do error handling
        self._buf += data
        while ':' in self._buf:
            length, rest = self._buf.split(':', 1)
            length = int(length)
            if len(rest) <= length:
                break
            string = rest[:length]
            self._buf = rest[length+1:]
            self.receiver(string)


class KeyPairReader(object):
    """
    I read keys and values as they come in sequence.
    """

    def __init__(self, receiver):
        """
        @param receiver: Function to be called with each key-value tuple.
        """
        self.receiver = receiver
        self._key = None


    def stringReceived(self, string):
        """
        Read either a key or value string.

        @param string: Either a key or value string.
        """
        if not self._key:
            self._key = string
        else:
            key = self._key
            self._key = None
            self.receiver((key, string))
