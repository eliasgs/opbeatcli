import unittest
import mock
import os
import subprocess
from opbeatcli.modprobes.release import (Module, Release)
from opbeatcli.modprobes import npm_probe

import sys

class MockPopen(object):
    def __init__(self, output):
        self.stdout = output 


class TestNpmProbe(unittest.TestCase):
    def empty_result(*args, **kwargs):
        result = os.fdopen(os.open('/dev/null', os.O_RDONLY))
        return MockPopen(result)

    def valid_result(*args, **kwargs):
        result = os.fdopen(os.open('tests/modprobes/fixtures/npm_probe',
                           os.O_RDONLY))
        return MockPopen(result)

    @mock.patch('opbeatcli.modprobes.npm_probe.exec_cmd')
    def test_npm_not_installed(self, exec_cmd):
        """
        Should return an empty list, if node is not istalled 
        """
        exec_cmd.return_value = []
        
        releases = npm_probe.run()
        self.assertEqual(releases, [])

    @mock.patch('subprocess.Popen')
    def test_no_modules_installed(self, Popen):
        """
        Should return an empty list if there are no node modules installed
        """
        Popen.side_effect = self.empty_result

        releases = npm_probe.run()
        self.assertEqual(releases, [])

    # 
    @mock.patch('subprocess.Popen')
    def test_installed_modules_as_list(self, Popen):
        """
        Should return a list of installed node modules     
        """
        Popen.side_effect = self.valid_result

        # see fixtures/npm_probe 
        expected = [
            Release(Module('express'), '3.0.4'),
            Release(Module('mocha'), '1.5.0'),
            Release(Module('nodemon'), '0.6.9'),
            Release(Module('npm'), '1.1.49')]

        # should reappear as both local and global modules are probed
        expected += expected

        releases = npm_probe.run()

        self.assertEqual(releases, expected)

