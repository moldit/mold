from twisted.internet.protocol import ProcessProtocol
from twisted.internet import defer, error
from zope.interface import implements

from mold.interface import ITrigger
from mold.error import TriggerDone


def tee(funcs):
    """
    Create a single function that will call each of C{funcs} when called.
    """
    def tee_func(*args, **kwargs):
        ret = []
        for func in funcs:
            try:
                response = func(*args, **kwargs)
                ret.append(response)
            except Exception as e:
                ret.append(e)
        return ret
    return tee_func



class SimpleProtocol(ProcessProtocol):
    """
    XXX

    @ivar done: A callback that will be called back with a ProcessDone instance
        or else errback with a ProcessTerminated instance.
    """

    _stdin_closed = False

    def __init__(self, catchall, outputReceivers=None, triggers=None):
        """
        @param catchall: A function to be called with output not sent to
            one of C{outputReceivers}.
        @param outputReceivers: A dictionary of file descriptor numbers
            to functions that will be called with each piece of data received
            on that file descriptor.
        @param triggers: A list of triggers.  See L{addTrigger} for more
            information.
        """
        self.done = defer.Deferred()

        self.catchall = catchall
        self.outputReceivers = outputReceivers or {}
        self._triggers = triggers or []


    def childDataReceived(self, childFD, data):
        receiver = self.outputReceivers.get(childFD, self.catchall)
        receiver(data)
        for trigger in list(self._triggers):
            try:
                trigger.childDataReceived(self, childFD, data)
            except TriggerDone:
                self.removeTrigger(trigger)
        
        if not self._triggers and not self._stdin_closed:
            self.transport.write('\x04')
            self.transport.closeStdin()
            self._stdin_closed = True


    def addTrigger(self, trigger):
        """
        Add a L{ITrigger} to receive all output and possibly do something
        useful with it.
        """
        self._triggers.append(trigger)


    def removeTrigger(self, trigger):
        """
        Remove a L{ITrigger} from receiving output.
        """
        self._triggers.remove(trigger)


    def processEnded(self, status):
        if isinstance(status.value, error.ProcessTerminated):
            self.done.errback(status.value)
        else:
            self.done.callback(status.value)



class TriggerInput(object):
    """
    I cause data to be written to a process protocol's stdin when a trigger
    condition is met.
    """

    implements(ITrigger)

    def __init__(self, stdin, trigger):
        self.sub_trigger = trigger
        self.stdin = stdin


    def childDataReceived(self, proto, childFD, data):
        try:
            self.sub_trigger.childDataReceived(proto, childFD, data)
        except TriggerDone:
            proto.transport.write(self.stdin)
            raise


class AnyString(object):
    """
    I raise L{TriggerDone} when one of a list of strings is found in the
    output of a process.
    """
    
    implements(ITrigger)

    def __init__(self, strings):
        self.strings = strings
        self.buffer = ''


    def childDataReceived(self, proto, childFD, data):
        self.buffer += data
        for string in self.strings:
            if string in self.buffer:
                raise TriggerDone()

