from .part2 import Part2, part2_normal, part2_normalx, unhooked


class Part1:
    def one(self):
        part2 = Part2()
        part2.cls_no_param()
        part2.cls_arg('cls_arg')
        part2.cls_kw(cls_x=99, cls_y=99, cls_z="99", my=21)
        part2.method_no_param()
        part2.method_arg('method_arg')
        part2.method_kw('method_kw')
        part2.static_no_param()
        part2.static_arg('static_arg1', 'static_arg2')
        part2.static_kw(99, 99)
        part2.unhooked()

        part2_normal(23)
        part2_normalx()
        unhooked()

    @classmethod
    def two(cls):
        Part2.cls_no_param()
        Part2.cls_arg('cls_arg')
        Part2.cls_kw(cls_x=99, cls_y=99, cls_z="99", my=21)

        ins = Part2()
        ins.method_no_param()
        ins.method_arg('method_arg')
        ins.method_kw('method_kw')

        Part2.static_no_param()
        Part2.static_arg('static_arg1', 'static_arg2')
        Part2.static_kw(99, 99)

        ins.unhooked()

        part2_normal(45)
        part2_normalx()
        unhooked()
