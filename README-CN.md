### 背景
1. 编写测试用例时，通常需要自己制造数据，在迭代时要不停更改数据。因此期望提取变更前一次运行的输入/输出，作为变更后的输入和预期输出值。

2. 期望获取多个rpc服务函数的入参及返回值，来作为1. 测试的初始数据或2. 作为mock rpc服务的入参及返回值。

### 设计目标
能便捷（可快速开关，快速变更）地获取1个或多个函数的输入/输出

### 设计方案
使用装饰器获得入参及返回值，参照unittest.mock重新绑定函数

### 使用方式
参考test文件夹
```python
from your_project import your_main_entry
from apihook import multi_hooker, LogInjectionBase, LogInjectionDataBase, api_hooker
from apihook.yaml_parser import yaml_hookers, yaml_dump_hookers
from apihook.log_parser import get_log_data


HOOK_MODE = None
hookers = multi_hooker()

common_hooker_1 = api_hooker('your_project.part3.ExpClass', include_attrs=['func3'])

if HOOK_MODE == 'specify hook in code':
    hookers.add_hook('your_project.part2.ExpClass', include_attrs=['clsmethod2'], injection=LogInjectionBase)
    hookers.add_hook('your_project.part2.ExpClass', include_attrs=['clsmethod2', 'func2', 'staticmethod2'])
    hookers.add_hook('your_project.part2', include_attrs=['normal_func'])
    hookers.add_hook('your_project.part2.normal_func2')
elif HOOK_MODE == 'inject param/result from log':
    hookers.add(common_hooker_1)
    hookers.add_hook('your_project.part2.ExpClass', include_attrs=['clsmethod2'], injection=LogInjectionDataBase, 
        injection_data=get_log_data('log.log'))
elif HOOK_MODE == 'specify hook from yaml':
    y_hookers= yaml_hookers('example.yaml')
    with y_hookers:
        your_main_entry()
    yaml_dump_hookers(y_hookers, file='example.yaml')

with hookers:  # function restored after exting scope
    your_main_entry()
```
1. api_hooker中指定hook模块/类的路径，不一定是对象原始代码所在路径，任一导入了此对象的路径皆可
2. 注意同一个函数使用多个injection时最后添加的最先生效
2. 对同一个函数可injection多次，因此要注意是否存在同一个函数非预期的重复hook
3. 可对调用大模块的函数输出特殊日志，如此可在处理日志时进行分割

### 使用场景
适用：
1. 想对某几个函数传入的参数和返回的结果进行处理，而不影响流程的运行。
2. 传给函数的参数为字符串，数字，列表等简单类型（或者可序列化，实现__getstate__,__setstate__，并可比较相等，实现__eq__），如此通过日志记录有意义

不适用：
1. 修改整个类的行为，需手动重写整个类，此时可直接使用unittest.mock

### 达成效果
1. 能极小的侵害源代码
2. 可达到类似模板的效果，自行组合就能适用不同的需求
3. 可将结果保存到日志，日志后续可对不同时间阶段的日志map/reduce

### 计划
1. **DONE** 支持协程
2. p1 测试多线程是否安全
3. **DONE** 支持需hook的函数配置为yaml，通过运行不同的配置记录不同信息，配置为空则等同于未hook任何函数
4. **DONE** hooker的target参数~~支持传入模块/类（现只能是字符串）~~现支持传入字符串/模块/类/函数
    ~~1. 代码迭代时由于hook的target是字符串，无法使用pycharm的find usage 和 refactor~~
5. **DONE** 日志解析，提取函数的入参及返回值。hook函数后，函数能查找匹配的入参并返回相应的出参。
    1. 使用LogInjectionBase或其继承类，运行一次程序
    2. 使用log_parser解析记录并保存到json文件
    3. 使用InjectionDataBase或其继承类替换LogInjectionBase，载入json文件，设为injection_data的值（所有InjectionDataBase共享这些数据），此时再运行程序就使用这些数据，而不再调用耗时/有副作用的原函数。
    
