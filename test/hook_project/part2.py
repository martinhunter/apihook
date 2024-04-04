class Part2:
    cls_attr = 'cls attr'
    init_attr = 'init-attr-of-class'

    def __init__(self):
        self.init_attr = 'init-attr-of-self'

    @classmethod
    def cls_no_param(cls):
        print('cls_no_param:', cls.init_attr)

    @classmethod
    def cls_arg(cls, c0):
        print('cls_arg:', c0, cls.init_attr)

    @classmethod
    def cls_kw(cls, cls_x=10, cls_y=30, cls_z="213", **kwargs):
        print('cls_kw:', cls_x, cls_y, cls_z, kwargs, cls.init_attr)

    def method_no_param(self):
        print('method_no_param:', self.init_attr)

    def method_arg(self, m0):
        print('method_arg:', m0, self.init_attr)

    def method_kw(self, method_x=21):
        print('method_kw:', method_x, self.init_attr)

    @staticmethod
    def static_no_param():
        print('static_no_param:')

    @staticmethod
    def static_arg(s0, s1):
        print('static_arg:', s0, s1)

    @staticmethod
    def static_kw(sta_x, sta_y=95, sta_z=33):
        print('static_kw:', sta_x, sta_y, sta_z)

    def unhooked(self):
        print('this is unhooked class func')


def part2_normal(part_n, part_o=92):
    print('normal2 %s---' % part_n, part_o)


def part2_normalx():
    print('normalx')


def unhooked():
    print('this is unhooked func')
