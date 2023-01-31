### 背景
仅在程序入口修改源码，以获取指定函数（例如调用rpc服务）的入参及返回值，可将结果保存到日志，
日志后续按不同时间阶段map/reduce

### 设计方案
使用装饰器获得入参及返回值，参照mock重新绑定函数

### 使用方式
```python
from your_project import run
from api_hook import multi_hooker, LogInjectionBase

hookers = multi_hooker()
hookers.add_hook('your_project.part2.ExpClass', include_attrs=['clsmethod2'], injection=LogInjectionBase)
hookers.add_hook('your_project.part2.ExpClass', include_attrs=['clsmethod2', 'func2', 'staticmethod2'])
hookers.add_hook('your_project.part2', include_attrs=['normal_func'])
hookers.add_hook('your_project.part2.normal_func2')
# hookers.add_hook('temp.part2.CONST')  # hook常量无意义
with hookers:  # 离开作用域后恢复
    run()
```
1. api_hooker中指定hook模块/类的路径
2. 对同一个函数可injection多次，因此要注意是否存在同一个函数非预期的重复hook
3. 可对调用大模块的函数输出特殊日志，如此可在处理日志时进行分割

### 计划
1. 支持协程
2. 测试多线程是否安全
3. 支持需hook的函数配置为yaml