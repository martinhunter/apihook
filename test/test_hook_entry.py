import unittest

from exceptions import HookEntryTypeErr
from hook_entry import multi_hooker, api_hooker, _dot_lookup, _get_target
from test.hook_project import run, async_run


class TestHookEntryWorks(unittest.TestCase):
    def test_integrated(self):
        hookers = multi_hooker()
        hookers.add_hook('test.hook_project.part2.Part2', includes=['cls2'])
        hookers.add_hook('test.hook_project.part2.Part2', includes=['cls2', 'func2', 'sta2'])
        hookers.add_hook('test.hook_project.part2', includes=['part2_normal'])
        hookers.add_hook('test.hook_project.part2.part2_normalx')
        hookers.add_hook('test.hook_project.part2.part2_normalx', injection=None)
        with hookers:
            run()
        run()

    def test_imported(self):
        import sys
        from test.hook_project.part2 import Part2, part2_normalx
        hookers = multi_hooker()
        hookers.add_hook(Part2, includes=['cls2'])
        hookers.add_hook(Part2, includes=['cls2', 'func2', 'sta2'])
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
        hookers.add_hook('test.hook_project.part2_async.AsyncPart2', injection=None)
        with hookers:
            await async_run()
        await async_run()


class TestHookEntryException(unittest.TestCase):
    def test_raise_hook_constant(self):
        hookers = multi_hooker()
        hooker = api_hooker('test.hook_project.part2.CONST')
        hookers.add(hooker)
        with self.assertRaises(HookEntryTypeErr):
            # check target type when start hook
            hookers.start_hook()
        hookers.rm_hook(hooker)

    def test_raise_hook_param(self):
        hookers = multi_hooker()
        hookers.add_hook('test.hook_project.part2.CONST')
        hookers.add_hook('test.hook_project.part2_async', includes=['AsyncPart2'])
        hookers.add_hook(None)
        for hooker in hookers:
            with self.assertRaises(HookEntryTypeErr):
                hooker.start_hook()

    def test_raise_hook_not_exist(self):
        hookers = multi_hooker()
        hookers.add_hook('test.hook_project.not_exist')
        with self.assertRaises(AttributeError):
            hookers.start_hook()


class TestImporter(unittest.TestCase):
    def test__dot_lookup(self):
        _dot_lookup('test', 'hook_project', 'test')

    def test__get_target(self):
        with self.assertRaises(TypeError):
            _get_target(3)


if __name__ == '__main__':
    unittest.main()
