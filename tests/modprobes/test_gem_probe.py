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
        self.stdout = os.fdopen(os.open('tests/modprobes/fixtures/gem_probe',
                                os.O_RDONLY))
        return self


class TestGemProbe(unittest.TestCase):
    @mock.patch('opbeatcli.modprobes.gem_probe.exec_cmd')
    def test_gem_not_installed(self, exec_cmd):
        """
        Should return an empty list the gem is not installed
        """
        exec_cmd.return_value = []
        
        releases = gem_probe.run()
        self.assertEqual(releases, [])

    @mock.patch('subprocess.Popen')
    def test_no_gems_installed(self, Popen):
        """
        Should return an empty list if there are no gems installed
        """
        Popen.return_value = MockPopen().empty_result()

        releases = gem_probe.run()
        self.assertEqual(releases, [])

    @mock.patch('subprocess.Popen')
    def test_installed_gems_as_list(self, Popen):
        """
        Should return a list of installed gems
        """
        Popen.return_value = MockPopen().valid_result()

        # see fixtures/gem_probe
        expected = [
            Release(Module('chunky_png', 'gem'), '1.2.8'),
            Release(Module('compass', 'gem'), '0.12.2'),
            Release(Module('fssm', 'gem'), '0.2.10'),
            Release(Module('sass', 'gem'), '3.2.7')]

        releases = gem_probe.run()
        self.assertEqual(releases, expected)

    @mock.patch('subprocess.Popen')
    def test_module_type(self, Popen):
        """
        Should send the proper module_type
        """
        Popen.return_value = MockPopen().valid_result()

        releases = gem_probe.run()
        for release in releases:
            self.assertEqual(release.module.module_type, 'gem')
