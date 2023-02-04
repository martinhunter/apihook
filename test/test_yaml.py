import os
import unittest

from test.hook_project import run
from yaml_parser import yaml_hookers, yaml_dump_hookers


class TestYamlHookWorks(unittest.TestCase):
    def setUp(self) -> None:
        self.yaml_file = os.path.join(os.path.dirname(__file__), 'hook_project/example.yaml')

    def test_yaml_loader(self):
        hookers = yaml_hookers(self.yaml_file)
        with hookers:
            run()
        run()

    def test_yaml_dump(self):
        dumped_file = 'dumped.yaml'
        hookers = yaml_hookers(self.yaml_file)
        yaml_dump_hookers(hookers, file=dumped_file)
        os.remove(dumped_file)


if __name__ == '__main__':
    unittest.main()
