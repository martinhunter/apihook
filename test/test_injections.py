import unittest

from hook_entry import multi_hooker
from injections import *
from test.hook_project import run, async_run


class InjPrint(InjectionBase):
    def hook_start(self, *args, **kwargs):
        print('Hook:', args, kwargs)


class MockPart3:
    def __init__(self, x):
        self.x = x

    def prove(self, one, two=11):
        return (one + two + self.x) * 100


class TestInjectionWorks(unittest.TestCase):
    def test_integrated(self):
        hookers = multi_hooker()
        hookers.add_hook('test.hook_project.part2.Part3', injection=MockPart3)
        hookers.add_hook('test.hook_project.part2.Part2', includes=[
            'cls_no_param', 'cls_arg', 'cls_kw', 'method_no_param', 'method_arg', 'method_kw', 'static_no_param',
            'static_arg', 'static_kw'
        ], injection=InjPrint)
        hookers.add_hook('test.hook_project.part2', includes=['part2_normal'], injection=InjectionDataNoException,
                         injection_data={'test.hook_project.part1.part2_normal': {
                             '(23,){}': 'value1', '(45,){}': 'value2'
                         }})
        hookers.add_hook('test.hook_project.part2.part2_normalx', injection=None)
        hookers.add_hook('test.hook_project.part2.CONST', injection=999)
        hookers.add_hook('test.hook_project.part2.const_var', injection={'changed_var': 'hooked'})
        with hookers:
            run()


class TestInjectionAsyncWorks(unittest.IsolatedAsyncioTestCase):
    async def test_integrated_async(self):
        hookers = multi_hooker()
        hookers.add_hook('test.hook_project.part2_async.AsyncPart2', includes=['cls2'], injection=InjChangeSkip)
        hookers.add_hook('test.hook_project.part2_async', includes=['async_part2_normal'])
        hookers.add_hook('test.hook_project.part2_async.async_part2_normalx', injection=InjectionDataNoException,
                         injection_data={'test.hook_project.part1.part2_normal': {
                             '(23,){}': 'value1', '(45,){}': 'value2'
                         }})
        with hookers:
            await async_run()
        await async_run()


if __name__ == '__main__':
    unittest.main()
