from yaml_parser import yaml_hookers
import unittest
from test.hook_project import run


class TestYamlHookEntry(unittest.TestCase):
    def test_integrated(self):
        with yaml_hookers('./hook_project/example.yaml'):
            run()
        run()




if __name__ == '__main__':
    unittest.main()
