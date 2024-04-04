import os
import unittest

from hook_entry import multi_hooker
from injections import LogInjectionBase
from log_parser import get_log_data, dump_data, load_data
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
        expected = {'hook_project.part1.Part2.cls_arg': {'3c41685a8f9f2136dbe0e2a6e4b0268e': None},
                    'hook_project.part1.Part2.method_arg': {'833ab21af8f8a08f5c3708fdc89c14ee': None},
                    'hook_project.part1.Part2.static_arg': {'e35a1adb33c39b80153cc7b70889cf4c': None}}
        actual = get_log_data(self.file)
        self.assertEqual(expected, actual)
        file = 'temp.json'
        dump_data(file, data=actual)
        actual = load_data(file)
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
