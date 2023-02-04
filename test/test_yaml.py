import os
import unittest

from test.hook_project import run
from yaml_parser import yaml_hookers


class TestYamlHookEntry(unittest.TestCase):
    def test_integrated(self):
        yaml_file = os.path.join(os.path.dirname(__file__), 'hook_project/example.yaml')
        with yaml_hookers(yaml_file):
            run()
        run()


if __name__ == '__main__':
    unittest.main()
