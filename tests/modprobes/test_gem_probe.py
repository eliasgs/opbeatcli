import unittest
import mock
import os
import subprocess
from opbeatcli.modprobes.release import (Module, Release)
from opbeatcli.modprobes import gem_probe

class MockPopen(object):
    def empty_result(self):
        self.stdout = os.fdopen(os.open('/dev/null', os.O_RDONLY))
        return self
    def valid_result(self):
        self.stdout = os.fdopen(os.open('tests/modprobes/fixtures/gem_probe', os.O_RDONLY))
        return self


class TestGemProbe(unittest.TestCase):
    # should return an empty list the gem is not installed
    @mock.patch('opbeatcli.modprobes.gem_probe.exec_cmd')
    def test_gem_not_installed(self, exec_cmd):
        exec_cmd.return_value = []
        
        releases = gem_probe.run()
        self.assertEqual(releases, [])

    # should return an empty list if there are no gems installed
    @mock.patch('subprocess.Popen')
    def test_no_gems_installed(self, Popen):
        Popen.return_value = MockPopen().empty_result()

        releases = gem_probe.run()
        self.assertEqual(releases, [])

    # should return a list of installed gems
    @mock.patch('subprocess.Popen')
    def test_installed_gems_as_list(self, Popen):
        Popen.return_value = MockPopen().valid_result()

        # see fixtures/gem_probe
        expected = [
            Release(Module('chunky_png'), '1.2.8'),
            Release(Module('compass'), '0.12.2'),
            Release(Module('fssm'), '0.2.10'),
            Release(Module('sass'), '3.2.7')]

        releases = gem_probe.run()
        self.assertEqual(releases, expected)

