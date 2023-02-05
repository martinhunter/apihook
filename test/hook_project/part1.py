from .part2 import Part2, part2_normal, part2_normalx, unhooked


class Part1:
    def one(self):
        part2 = Part2()
        part2.cls2(21, 44, c=22, one='x32', two='cx3', three='x45')
        part2.func2()
        part2.sta2()
        part2.unhooked()

        part2_normal(23)
        part2_normalx()
        unhooked()

    @classmethod
    def two(cls):
        part2 = Part2()
        part2.cls2()
        part2.func2()
        part2.sta2()
        part2.unhooked()

        part2_normal(45)
        part2_normalx()
        unhooked()
