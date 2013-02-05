

__all__ = ['ProcessStream', 'ProcessStarted', 'ProcessEnded']


from collections import namedtuple



class ProcessStream(namedtuple('ProcessStream',
    ['pid', 'fd', 'data'])):
    """
    I am a message indicating that data was written to a process pipe.
    """



class ProcessStarted(namedtuple('ProcessStarted',
    ['ppid', 'pid', 'executable', 'args', 'env', 'path', 'uid', 'gid', 'usePTY'])):
    """
    I am a message indicating that a process was started.
    """



class ProcessEnded(namedtuple('ProcessEnded',
    ['pid', 'exitcode', 'signal'])):
    """
    I am a message indicating that a process ended.
    """


