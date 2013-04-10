import unittest
import mock
import os
import subprocess
from opbeatcli.modprobes.release import (Module, Release)
from opbeatcli.modprobes import dpkg_probe

class MockPopen(object):
    def empty_result(self):
        self.stdout = os.fdopen(os.open('/dev/null', os.O_RDONLY))
        return self
    def valid_result(self):
        self.stdout = os.fdopen(os.open('tests/modprobes/fixtures/dpkg_probe', os.O_RDONLY))
        return self


class TestGemProbe(unittest.TestCase):
    # should return an empty list the gem is not installed
    # @mock.patch('opbeatcli.modprobes.dpkg_probe.exec_cmd')
    # def test_dpkg_not_installed(self, exec_cmd):
    #     exec_cmd.return_value = []
    #     
    #     releases = dpkg_probe.run()
    #     self.assertEqual(releases, [])

    # should return an empty list if there are no gems installed
    @mock.patch('subprocess.Popen')
    def test_no_packages_installed(self, Popen):
        Popen.return_value = MockPopen().empty_result()

        releases = dpkg_probe.run()
        self.assertEqual(releases, [])

    # should return a list of installed gems
    @mock.patch('subprocess.Popen')
    def test_installed_packages_as_list(self, Popen):
        Popen.return_value = MockPopen().valid_result()

        # see fixtures/gem_probe
        expected = [
            Release(Module('accountsservice'), '0.6.15-2ubuntu9'),
            Release(Module('adduser'), '3.113ubuntu2'),
            Release(Module('apparmor'), '2.7.102-0ubuntu3'),
            Release(Module('apt'), '0.8.16~exp12ubuntu10')]

        releases = dpkg_probe.run()
        self.assertEqual(releases, expected)

