class Part2:
    @classmethod
    def cls2(cls, x=10, y=30, c="213", **kwargs):
        print('cls2 ---')

    def func2(self):
        print('func2 ---')

    @staticmethod
    def sta2():
        print('sta2 ---')

    def unhooked(self):
        print('this is unhooked class func')


def part2_normal(n):
    print('normal2 %s---' % n)


def part2_normalx():
    print('normalx ---')


def unhooked():
    print('this is unhooked func')


CONST = 321
