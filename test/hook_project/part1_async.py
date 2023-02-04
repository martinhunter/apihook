from .part2_async import *


class AsyncPart1:
    async def async_one(self):
        part2 = AsyncPart2()
        await part2.cls2()
        await part2.func2()
        await part2.sta2()
        await part2.unhooked()

        await async_part2_normal()
        await async_part2_normalx()
        await async_unhooked()

    @classmethod
    async def async_two(cls):
        part2 = AsyncPart2()
        await part2.cls2()
        await part2.func2()
        await part2.sta2()
        await part2.unhooked()

        await async_part2_normal()
        await async_part2_normalx()
        await async_unhooked()
