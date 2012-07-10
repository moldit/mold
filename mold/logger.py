from zope.interface import implements
from datetime import datetime
import json

from mold.interface import ILogger


class FileLogger:
    """
    I log to files.
    """
    
    implements(ILogger)


    fileFactory = lambda: 'xXX'


    def __init__(self):
        self._files = {}


    def _getFile(self, channel):
        if channel not in self._files:
            self._files[channel] = self.fileFactory()
        return self._files[channel]


    def msg(self, message, channel=None):
        """
        XXX
        """
        fh = self._getFile(channel)
        fh.write(message + '\n')


    def json(self, data, channel=None):
        """
        XXX
        """
        fh = self._getFile(channel)
        fh.write(json.dumps(data) + '\n')