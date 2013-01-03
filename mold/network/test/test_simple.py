from twisted.trial.unittest import TestCase



from mold.network.simple import AmpMinion, AmpMaster
from mold.process import SimpleProtocol



class SingleUseRunner:


    def __init__(self, response):
        self.name = None
        self.args = None
        self.stdin = None
        self._response = response


    def run(self, name, args, stdin):
        self.name = name
        self.args = args
        self.stdin = stdin
        return self._response



class AmpMinionTest(TestCase):


    def test_init(self):
        """
        Should accept a runner
        """
        m = AmpMinion('foo')
        self.assertEqual(m.script_runner, 'foo')


    def test_run(self):
        """
        You can run scripts
        """
        runner = SingleUseRunner(