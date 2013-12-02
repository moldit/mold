from twisted.trial.unittest import TestCase

from zope.interface.verify import verifyObject

from mock import MagicMock

from mold.error import TriggerDone
from mold.interface import ITrigger
from mold.transport.common import tee, SimpleProtocol, TriggerInput, AnyString


class teeTest(TestCase):


    def test_split(self):
        """
        tee() should make a callable that calls other callables.
        """
        lista = []
        listb = []
        f = tee([lista.append, listb.append])
        r = f('foo')
        self.assertEqual(lista, ['foo'])
        self.assertEqual(listb, ['foo'])
        self.assertEqual(r, [None, None])


    def test_error(self):
        """
        An error in one function should not cause an error on another.
        """
        lista = []
        listb = []
        f = tee([lista.remove, listb.append])
        r = f('foo')
        self.assertEqual(lista, [])
        self.assertEqual(listb, ['foo'])
        self.assertTrue(isinstance(r[0], Exception))


class AnyStringTest(TestCase):

    
    def test_ITrigger(self):
        verifyObject(ITrigger, AnyString(['foo', 'bar']))


    def test_match(self):
        """
        When an exact string is matched, raise TriggerDone.
        """
        t = AnyString(['foo'])
        self.assertRaises(TriggerDone, t.childDataReceived, None, None, 'foo')


    def test_partial(self):
        """
        When a string is encountered in pieces, raise TriggerDone.
        """
        t = AnyString(['foo'])
        t.childDataReceived(None, None, 'afo')
        self.assertRaises(TriggerDone, t.childDataReceived, None, None, 'oom')


    def test_multi(self):
        """
        Either of the strings can cause the trigger to happen.
        """
        t = AnyString(['foo', 'bar'])
        t.childDataReceived(None, None, 'foba')
        self.assertRaises(TriggerDone, t.childDataReceived, None, None, 'r')



class TriggerInputTest(TestCase):


    def test_ITrigger(self):
        verifyObject(ITrigger, TriggerInput('foo', 'trigger'))


    def test_passDataOn(self):
        """
        All data should be passed on to the sub trigger.
        """
        sub_trigger = MagicMock()
        t = TriggerInput('foo', sub_trigger)
        t.childDataReceived('proto', 2, 'something')
        sub_trigger.childDataReceived.assert_called_once_with(
            'proto', 2, 'something')


    def test_write_TriggerDone(self):
        """
        When teh sub strigger raises L{TriggerDone}, write the stdin to the
        protocol's transport.
        """
        sub_trigger = MagicMock()
        sub_trigger.childDataReceived.side_effect = TriggerDone()

        t = TriggerInput('foo', sub_trigger)

        proto = MagicMock()
        self.assertRaises(TriggerDone, t.childDataReceived, proto, 1,
                          'something')
        proto.transport.write.assert_called_once_with('foo')



class SimpleProtocolTest(TestCase):


    def test_streamOutput(self):
        """
        All data received should be written out to functions passed in at
        init.
        """
        stdout = []
        stderr = []
        catchall = []

        proto = SimpleProtocol(catchall.append, {
            1: stdout.append,
            2: stderr.append,
        })
        proto.transport = MagicMock()

        proto.childDataReceived(1, 'some stdout')
        proto.childDataReceived(2, 'some stderr')
        proto.childDataReceived(3, 'some channel 3')

        self.assertEqual(stdout, ['some stdout'])
        self.assertEqual(stderr, ['some stderr'])
        self.assertEqual(catchall, ['some channel 3'])


    def test_justCatchall(self):
        """
        If only a catchall is provided, all output will go to that.
        """
        data = []
        proto = SimpleProtocol(data.append)
        proto.transport = MagicMock()
        proto.childDataReceived(1, 'some stdout')
        proto.childDataReceived(2, 'some stderr')
        self.assertEqual(data, ['some stdout', 'some stderr'])


    def test_addTrigger(self):
        """
        addTrigger registers a function to be called for every bit of output
        received on a specific channel.
        """
        data = []
        proto = SimpleProtocol(data.append)
        proto.transport = MagicMock()

        trigger = MagicMock()
        proto.addTrigger(trigger)

        proto.childDataReceived(1, 'foo')
        trigger.childDataReceived.assert_called_once_with(proto, 1, 'foo')


    def test_removeTrigger(self):
        """
        removeTrigger removes a trigger from a proto.
        """
        proto = SimpleProtocol(lambda x: None)
        proto.transport = MagicMock()

        trigger = MagicMock()
        proto.addTrigger(trigger)
        proto.removeTrigger(trigger)

        proto.childDataReceived(1, 'foo')
        self.assertEqual(trigger.childDataReceived.call_count, 0)


    def test_TriggerDone(self):
        """
        A trigger raising TriggerDone should cause the trigger to be removed
        """
        proto = SimpleProtocol(lambda x: None)
        proto.transport = MagicMock()

        trigger = MagicMock()
        trigger.childDataReceived.side_effect = TriggerDone('foo')
        proto.addTrigger(trigger)

        proto.childDataReceived(1, 'foo')
        trigger.childDataReceived.assert_called_once_with(proto, 1, 'foo')
        proto.transport.closeStdin.assert_called_once_with()
        trigger.childDataReceived.reset_mock()

        proto.childDataReceived(1, 'bar')
        self.assertEqual(trigger.childDataReceived.call_count, 0, "Should not "
                         "have called the trigger again, because it signalled "
                         "through raising TriggerDone that it is done.")


    def test_closeStdinIfNoTriggers(self):
        """
        If some data is received and there are no triggers, close stdin
        """
        proto = SimpleProtocol(lambda x: None)
        proto.transport = MagicMock()
        proto.childDataReceived(1, 'foo')
        proto.transport.closeStdin.assert_called_once_with()
