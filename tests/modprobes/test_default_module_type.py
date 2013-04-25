import unittest
from opbeatcli.modprobes.release import Module


class TestDefaultModuleType(unittest.TestCase):
    def test_defualt_module_type(self):
        """
        Should have 'egg' as a default module_type
        """
        module = Module('test_module')

        self.assertEqual(module.module_type, 'egg')
