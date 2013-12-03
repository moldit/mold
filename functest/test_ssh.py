from twisted.trial.unittest import TestCase, SkipTest
from twisted.internet import utils, defer
from twisted.python.procutils import which
from twisted.python import log

from mold.transport.test.mixin import FunctionalConnectionTestMixin
from mold.transport.ssh import SSHConnectionMaker

DOCKER = which('docker')
if DOCKER:
    DOCKER = DOCKER[0]


class SSHConnectionTransportTest(FunctionalConnectionTestMixin, TestCase):

    timeout = 2

    def killDockerContainer(self, container_id):
        log.msg('Killing container %s' % (container_id,), system='docker')
        return utils.getProcessOutputAndValue(
            DOCKER,
            ['kill', container_id])

    @defer.inlineCallbacks
    def getConnection(self):
        maker = SSHConnectionMaker()
        if not DOCKER:
            raise SkipTest('docker is not installed')

        # Start a docker container.
        log.msg('Spawning container...', system='docker')
        stdout, sdterr, rc = yield utils.getProcessOutputAndValue(
            DOCKER,
            ['run', '-p', '22', '-d', 'moldit/ubuntu-ssh'],
        )
        if rc != 0:
            self.fail("Could not spawn docker instance:\n%s\n%s" % (
                      stdout, stderr))
        container_id = stdout.strip()
        log.msg('Spawned container %s' % (container_id,), system='docker')
        self.addCleanup(self.killDockerContainer, container_id)

        # Generate an SSH uri for connecting to the container.
        stdout, stderr, rc = yield utils.getProcessOutputAndValue(
            DOCKER,
            ['port', container_id, '22'],
        )
        port = int(stdout.strip().split(':')[-1])
        uri = 'ssh://mold:mold@127.0.0.1:%d' % (port,)
        log.msg('Generated SSH URI: %r' % (uri,))
        conn = yield maker.getConnection(uri)
        defer.returnValue(conn)
