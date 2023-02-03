### 背景
期望获取多个rpc服务函数的入参及返回值，来作为1. 测试的初始数据或2. 作为mock rpc服务的入参及返回值。

### 设计方案
使用装饰器获得入参及返回值，参照mock重新绑定函数

### 使用方式
```python
from your_project import run
from api_hook import multi_hooker, LogInjectionBase, api_hooker

HOOK_PATTERN = 1
hookers = multi_hooker()

common_hooker_1 = api_hooker('your_project.part3.ExpClass', include_attrs=['func3'])

if HOOK_PATTERN == 1:
    hookers.add_hook('your_project.part2.ExpClass', include_attrs=['clsmethod2'], injection=LogInjectionBase)
    hookers.add_hook('your_project.part2.ExpClass', include_attrs=['clsmethod2', 'func2', 'staticmethod2'])
    hookers.add_hook('your_project.part2', include_attrs=['normal_func'])
    hookers.add_hook('your_project.part2.normal_func2')
elif HOOK_PATTERN == 2:
    hookers.add(common_hooker_1)
    hookers.add_hook('your_project.part2.ExpClass', include_attrs=['clsmethod2'], injection=LogInjectionBase)
else:
    pass
# hookers.add_hook('temp.part2.CONST')  # hook常量无意义
with hookers:  # 离开作用域后恢复
    run()
```
1. api_hooker中指定hook模块/类的路径，不一定是对象原始代码所在路径，任一导入了此对象的路径皆可
2. 注意同一个函数使用多个injection时最后添加的最先生效
2. 对同一个函数可injection多次，因此要注意是否存在同一个函数非预期的重复hook
3. 可对调用大模块的函数输出特殊日志，如此可在处理日志时进行分割

### 使用场景
适用：
1. 想对某几个函数传入的参数和返回的结果进行处理，而不影响流程的运行。
2. 传给函数的参数为字符串，数字，列表等简单类型，如此通过日志记录（序列化）有意义

不适用：
1. 修改整个类的行为，需手动重写整个类，此时可直接使用unittest.mock

### 达成效果
1. 能极小的侵害源代码
2. 可达到类似模板的效果，自行组合就能适用不同的需求
3. 可将结果保存到日志，日志后续可对不同时间阶段的日志map/reduce

### 计划
1. **DONE** p0 支持协程
2. p1 测试多线程是否安全
3. **DONE** p0 支持需hook的函数配置为yaml，通过运行不同的配置记录不同信息，配置为空则等同于未hook任何函数
4. **DONE** p0 hooker的target参数~~支持传入模块/类（现只能是字符串）~~现支持传入字符串/模块/类/函数
    ~~1. 代码迭代时由于hook的target是字符串，无法使用pycharm的find usage 和 refactor~~
5. 日志解析，提取函数的入参及返回值。hook函数后，函数能查找匹配的入参并返回相应的出参
