import unittest

from hook_entry import multi_hooker
from injections import *
from test.hook_project import run


class TestInjectionWorks(unittest.TestCase):
    def test_integrated(self):
        hookers = multi_hooker()
        hookers.add_hook('test.hook_project.part2.Part2', includes=['cls2'], injection=LogInjectionBase)
        hookers.add_hook('test.hook_project.part2.Part2', includes=['cls2', 'func2', 'sta2'])
        hookers.add_hook('test.hook_project.part2', includes=['part2_normal'], injection=InjectionDataNoException,
                         injection_data={})
        hookers.add_hook('test.hook_project.part2.part2_normalx')
        with hookers:
            run()


if __name__ == '__main__':
    unittest.main()
