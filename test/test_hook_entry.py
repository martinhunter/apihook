import unittest

from hook_entry import multi_hooker, api_hooker
from test.hook_project import run, async_run


class TestHookEntryWorks(unittest.TestCase):
    def test_integrated(self):
        hookers = multi_hooker()
        hookers.add_hook('test.hook_project.part2.Part2', includes=['cls2'])
        hookers.add_hook('test.hook_project.part2.Part2', includes=['cls2', 'func2', 'sta2'])
        hookers.add_hook('test.hook_project.part2', includes=['part2_normal'])
        hookers.add_hook('test.hook_project.part2.part2_normalx')
        with hookers:
            run()
        run()

    def test_integrated_import(self):
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
        with hookers:
            await async_run()
        await async_run()


class TestHookEntryLost(unittest.TestCase):
    def test_raise_hook_constant(self):
        hookers = multi_hooker()
        hooker = api_hooker('test.hook_project.part2.CONST')
        hookers.add(hooker)
        with self.assertRaises(Exception):
            # check target type when start hook
            hookers.start_hook()

        hookers.rm_hook(hooker)
        hookers.add_hook('test.hook_project.part2_async', injection=None)
        with self.assertRaises(Exception):
            hookers.start_hook()



    def test_raise_hook_not_exist(self):
        hookers = multi_hooker()
        hookers.add_hook('test.hook_project.not_exist')
        with self.assertRaises(Exception):
            hookers.start_hook()




if __name__ == '__main__':
    unittest.main()
