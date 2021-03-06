import unittest
from opbeatcli.utils.exec_cmd import exec_cmd

class TestExecCmd(unittest.TestCase):
    def test_empty(self):
        output = exec_cmd('tail /dev/null')
        # Check if empty
        self.assertEqual(next(output, None), None)

    def test_error(self):
        output = exec_cmd('this_is_not_a_valid_command')
        self.assertEqual(next(output, None), None)

    def test_invalid(self):
        output = exec_cmd('ls this_is_not_a_file')
        self.assertEqual(next(output, None), None)

    def test_correct(self):
        output = exec_cmd('printf test')
        result = ''.join(output)
        self.assertEqual(result, 'test')

    def test_working_dir(self):
        output = exec_cmd('cat exec_cmd', 'tests/utils/fixtures')
        result = ''.join(output)
        self.assertEqual(result, 'test')
