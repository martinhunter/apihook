### 背景
仅在程序入口修改源码，记录指定函数（例如调用rpc服务）的入参及返回值

### 使用方式
```python
from your_project import run
from api_hook import api_hooker,multi_hooker

hookers = multi_hooker()
hookers.add_hook('your_project.part2.Part2', include_attrs=['clsmethod2'], injection=TestInjection)
hookers.add_hook('your_project.part2.Part2', include_attrs=['clsmethod2', 'func2', 'staticmethod2'])
hookers.add_hook('your_project.part2', include_attrs=['part2_normal'])
hookers.add_hook('your_project.part2.part2_normalx')
# hookers.add_hook('temp.part2.CONST')  # hook常量无意义
with hookers:
    run()
```
1. api_hooker中指定hook模块/类的路径
2. 对同一个函数可injection多次