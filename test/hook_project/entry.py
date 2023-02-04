from .part1 import Part1
from .part1_async import AsyncPart1


def run():
    p = Part1()
    print('1~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    p.one()
    print('2~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    p.two()


async def async_run():
    async_p = AsyncPart1()
    print('3~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    await async_p.async_one()
    print('4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    await async_p.async_two()

