import os
import unittest

from hook_entry import multi_hooker
from injections import LogInjectionBase
from log_parser import get_log_data
from test.hook_project import run


class TestLogParserWorks(unittest.TestCase):
    def setUp(self) -> None:
        self.file = LogInjectionBase.file
        if os.path.isfile(self.file):
            os.remove(self.file)
        hookers = multi_hooker()
        hookers.add_hook('test.hook_project.part2.Part2', includes=['cls2'], injection=LogInjectionBase)
        hookers.add_hook('test.hook_project.part2.Part2', includes=['cls2'], injection=LogInjectionBase)
        with hookers:
            run()

    def test_log_data(self):
        expected = {'hook_project.part1.Part2.cls2': {'4734ea57213f855977b49c8bf90fe936': None,
                                                      '11e7903cf562f028d788fc601ffc9a04': None}}
        actual = get_log_data(self.file)
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
