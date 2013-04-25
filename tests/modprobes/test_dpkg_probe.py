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
        self.stdout = os.fdopen(os.open('tests/modprobes/fixtures/dpkg_probe',
                                os.O_RDONLY))
        return self


class TestDebianProbe(unittest.TestCase):
    @mock.patch('opbeatcli.modprobes.dpkg_probe.exec_cmd')
    def test_dpkg_not_installed(self, exec_cmd):
        """
        Should return an empty list if not on dpkg system
        """
        exec_cmd.return_value = []
        
        releases = dpkg_probe.run()
        self.assertEqual(releases, [])

    @mock.patch('subprocess.Popen')
    def test_no_packages_installed(self, Popen):
        """
        Should return an empty list if there are no packages installed
        """
        Popen.return_value = MockPopen().empty_result()

        releases = dpkg_probe.run()
        self.assertEqual(releases, [])

    @mock.patch('subprocess.Popen')
    def test_installed_packages_as_list(self, Popen):
        """
        Should return a list of installed packages
        """
        Popen.return_value = MockPopen().valid_result()

        # see fixtures/dpkg_probe
        expected = [
            Release(Module('accountsservice', 'deb'), '0.6.15-2ubuntu9'),
            Release(Module('adduser', 'deb'), '3.113ubuntu2'),
            Release(Module('apparmor', 'deb'), '2.7.102-0ubuntu3'),
            Release(Module('apt', 'deb'), '0.8.16~exp12ubuntu10')]

        releases = dpkg_probe.run()
        self.assertEqual(releases, expected)

    @mock.patch('subprocess.Popen')
    def test_module_type(self, Popen):
        """
        Should send the proper module_type
        """
        Popen.return_value = MockPopen().valid_result()

        releases = dpkg_probe.run()
        for release in releases:
            self.assertEqual(release.module.module_type, 'deb')
