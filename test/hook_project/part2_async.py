import asyncio


class AsyncPart2:
    @classmethod
    async def cls2(cls):
        print('cls2 async ---')
        await asyncio.sleep(0.001)

    async def func2(self):
        print('func2 async ---')
        await asyncio.sleep(0.001)

    @staticmethod
    async def sta2():
        print('sta2 async ---')
        await asyncio.sleep(0.001)

    async def unhooked(self):
        print('this is unhooked class func async ')
        await asyncio.sleep(0.001)


async def async_part2_normal():
    print('normal2 async ---')
    await asyncio.sleep(0.001)


async def async_part2_normalx():
    print('normalx async ---')
    await asyncio.sleep(0.001)


async def async_unhooked():
    print('this is unhooked func async ')
    await asyncio.sleep(0.001)


async_CONST = 321
