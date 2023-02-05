import unittest

from hook_entry import multi_hooker
from injections import *
from test.hook_project import run, async_run


class InjectionSkip(InjectionBase):
    skip_func = True
    change_result = True


class TestInjectionWorks(unittest.TestCase):
    def test_integrated(self):
        hookers = multi_hooker()
        hookers.add_hook('test.hook_project.part2.Part2', includes=['cls2'], injection=InjectionSkip)
        hookers.add_hook('test.hook_project.part2.Part2', includes=['cls2'], injection=LogInjectionBase)
        hookers.add_hook('test.hook_project.part2', includes=['part2_normal'], injection=InjectionDataNoException,
                         injection_data={'test.hook_project.part1.part2_normal': {
                             '(23,){}': 'value1', '(45,){}': 'value2'
                         }})
        hookers.add_hook('test.hook_project.part2.part2_normalx', injection=None)
        with hookers:
            run()


class TestInjectionAsyncWorks(unittest.IsolatedAsyncioTestCase):
    async def test_integrated_async(self):
        hookers = multi_hooker()
        hookers.add_hook('test.hook_project.part2_async.AsyncPart2', includes=['cls2'], injection=InjectionSkip)
        hookers.add_hook('test.hook_project.part2_async', includes=['async_part2_normal'])
        hookers.add_hook('test.hook_project.part2_async.async_part2_normalx', injection=InjectionDataNoException,
                         injection_data={'test.hook_project.part1.part2_normal': {
                             '(23,){}': 'value1', '(45,){}': 'value2'
                         }})
        hookers.add_hook('test.hook_project.part2_async.AsyncPart2', injection=None)
        with hookers:
            await async_run()
        await async_run()


if __name__ == '__main__':
    unittest.main()
