import unittest
from test.hook_project import run, async_run

from hook_entry import multi_hooker


class TestHookEntry(unittest.TestCase):
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
        from test.hook_project.part2 import Part2, part2_normalx
        hookers = multi_hooker()
        hookers.add_hook(Part2, includes=['cls2'])
        hookers.add_hook(Part2, includes=['cls2', 'func2', 'sta2'])
        hookers.add_hook('test.hook_project.part2', includes=['part2_normal'])
        hookers.add_hook(part2_normalx)
        with hookers:
            run()
        run()


class TestHookEntryAsync(unittest.IsolatedAsyncioTestCase):
    async def test_integrated_async(self):
        hookers = multi_hooker()
        hookers.add_hook('test.hook_project.part2_async.AsyncPart2', includes=['cls2'])
        hookers.add_hook('test.hook_project.part2_async.AsyncPart2', includes=['cls2', 'func2', 'sta2'])
        hookers.add_hook('test.hook_project.part2_async', includes=['async_part2_normal'])
        hookers.add_hook('test.hook_project.part2_async.async_part2_normalx')
        # hookers.add_hook('temp.part2.CONST')
        with hookers:
            await async_run()
        await async_run()


if __name__ == '__main__':
    unittest.main()

