import os
import unittest

from hook_entry import multi_hooker
from injections import LogInjectionBase
from log_parser import get_log_data, load_data, dump_data
from test.hook_project import run


class TestLogParserWorks(unittest.TestCase):
    def setUp(self) -> None:
        self.file = LogInjectionBase.file
        if os.path.isfile(self.file):
            os.remove(self.file)
        hookers = multi_hooker()
        hookers.add_hook('test.hook_project.part2.Part2', includes=['cls_arg'], injection=LogInjectionBase)
        hookers.add_hook('test.hook_project.part2.Part2', includes=['cls_arg'], injection=LogInjectionBase)
        hookers.add_hook('test.hook_project.part2.Part2', includes=['cls_arg'], injection=LogInjectionBase)
        hookers.add_hook('test.hook_project.part2.Part2', includes=['cls_arg'], injection=LogInjectionBase)
        hookers.add_hook('test.hook_project.part2.Part2', includes=['method_arg'], injection=LogInjectionBase)
        hookers.add_hook('test.hook_project.part2.Part2', includes=['method_arg'], injection=LogInjectionBase)
        hookers.add_hook('test.hook_project.part2.Part2', includes=['method_arg'], injection=LogInjectionBase)
        hookers.add_hook('test.hook_project.part2.Part2', includes=['method_arg'], injection=LogInjectionBase)
        hookers.add_hook('test.hook_project.part2.Part2', includes=['static_arg'], injection=LogInjectionBase)
        hookers.add_hook('test.hook_project.part2.Part2', includes=['static_arg'], injection=LogInjectionBase)
        hookers.add_hook('test.hook_project.part2.Part2', includes=['static_arg'], injection=LogInjectionBase)
        hookers.add_hook('test.hook_project.part2.Part2', includes=['static_arg'], injection=LogInjectionBase)
        with hookers:
            run()

    def test_log_data(self):
        expected = {'hook_project.part1.Part2.cls_arg': {'3c41685a8f9f2136dbe0e2a6e4b0268e': None,
                                                         '78a1edbcd10952f67817a92c45a8102c': None}}
        # actual = get_log_data(self.file)
        # self.assertEqual(expected, actual)
        # file = 'temp.json'
        # dump_data(file, data=actual)
        # actual = load_data(file)
        # self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
