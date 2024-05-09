import unittest

from hook_entry import multi_hooker, _get_target
from test.hook_project import run, async_run


class TestHookEntryWorks(unittest.TestCase):
    def test_integrated(self):
        hookers = multi_hooker()
        hookers.add_hook('test.hook_project.part2.Part2', includes=['cls_kw'])
        hookers.add_hook('test.hook_project.part2.Part2', includes=['cls_kw', 'method_kw', 'static_kw'])
        hookers.add_hook('test.hook_project.part2', includes=['part2_normal'])
        hookers.add_hook('test.hook_project.part2.part2_normalx')
        hookers.add_hook('test.hook_project.part2.part2_normalx', injection=None)
        hookers.add_hook('test.hook_project.part2.CONST')
        hookers.add_hook('test.hook_project.part2.const_var')
        hookers2 = multi_hooker()
        hookers2.add_hook('test.hook_project.part2.Part2', includes=['cls_kw'])
        hookers2.add_hook('test.hook_project.part2.Part2', includes=['cls_kw', 'method_kw', 'static_kw'])
        hookers2.add_hook('test.hook_project.part2', includes=['part2_normal'])
        hookers2.add_hook('test.hook_project.part2.part2_normalx')
        hookers2.add_hook('test.hook_project.part2.part2_normalx', injection=None)
        hookers2.add_hook('test.hook_project.part2.CONST', replace=True)
        hookers2.add_hook('test.hook_project.part2.const_var', replace=True)
        with hookers as h:
            with hookers2 as h2:
                run()

    def test_const(self):
        hookers = multi_hooker()
        hookers.add_hook('test.hook_project.part2.CONST', injection=22, replace=True)
        with hookers:
            run()

    def test_imported(self):
        import sys
        from test.hook_project.part2 import Part2, part2_normalx
        hookers = multi_hooker()
        hookers.add_hook(Part2, includes=['cls_kw'])
        hookers.add_hook(Part2, includes=['cls_kw', 'method_kw', 'static_kw'])
        hookers.add_hook(sys.modules['test.hook_project.part2'], includes=['part2_normal'])
        hookers.add_hook(part2_normalx)
        with hookers:
            run()
        run()


class TestHookEntryAsyncWorks(unittest.IsolatedAsyncioTestCase):
    async def test_integrated_async(self):
        hookers = multi_hooker()
        hookers.add_hook('test.hook_project.part2_async.AsyncPart2', includes=['cls2'])
        hookers.add_hook('test.hook_project.part2_async.AsyncPart2', includes=['cls2', 'func2', 'sta2'])
        hookers.add_hook('test.hook_project.part2_async', includes=['async_part2_normal'])
        hookers.add_hook('test.hook_project.part2_async.async_part2_normalx')
        hookers.add_hook('test.hook_project.part2_async', injection=None)
        with hookers:
            await async_run()
        await async_run()


class TestHookEntryException(unittest.TestCase):
    def test_raise_hook_not_exist(self):
        hookers = multi_hooker()
        hookers.add_hook('test.hook_project.not_exist')
        with self.assertRaises(AttributeError):
            hookers.start_hook()


class TestImporter(unittest.TestCase):
    def test_get_target(self):
        with self.assertRaises(TypeError):
            _get_target(3)


if __name__ == '__main__':
    unittest.main()
