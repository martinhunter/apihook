# apihook
> dynamically hook python functions params and results

## usable situations
1. run your program once and record params/results for unittest
2. run your program once and record params/results to mock api calls

## usage
e.g.
```python
from your_project import your_main_entry
import sys
sys.path.insert(0, r'D:\coding\pyprojects\mylibs')  # apihook在mylibs文件夹下
from api_hook import multi_hooker, LogInjectionBase, LogInjectionDataBase, api_hooker, BaseObjectFilter, condition_hookers
from api_hook.yaml_parser import yaml_hookers, yaml_dump_hookers
from api_hook.log_parser import get_log_data


HOOK_MODE = None


if HOOK_MODE == 'specify hook in code':
    hookers = multi_hooker()
    hookers.add_hook('your_project.part2.ExpClass', include_attrs=['clsmethod2'], injection=LogInjectionBase)
    hookers.add_hook('your_project.part2.ExpClass', include_attrs=['clsmethod2', 'func2', 'staticmethod2'])
    hookers.add_hook('your_project.part2', include_attrs=['normal_func'])
    hookers.add_hook('your_project.part2.normal_func2')
    with hookers:  # function restored after exting scope
        your_main_entry()
elif HOOK_MODE == 'inject param/result from log':
    hookers = multi_hooker()
    common_hooker_1 = api_hooker('your_project.part3.ExpClass', include_attrs=['func3'])
    hookers.add(common_hooker_1)
    hookers.add_hook('your_project.part2.ExpClass', include_attrs=['clsmethod2'], injection=LogInjectionDataBase, 
        injection_data=get_log_data('log.log'))
    with hookers:  # function restored after exting scope
        your_main_entry()
elif HOOK_MODE == 'specify hook from yaml':
    y_hookers= yaml_hookers('example.yaml')
    with y_hookers:
        your_main_entry()
    yaml_dump_hookers(y_hookers, file='example.yaml')
elif HOOK_MODE == 'find class or function that match filter':
    import sys
    sys.path.insert(0, r'D:\coding\pyprojects\quick_projects')
    from temp.one.temp1 import A
    class F(BaseObjectFilter):
        def filter(self, object_name, value):
            if isinstance(value, type) and issubclass(value, A):
                return self.create(object_name)
    
    hookers = condition_hookers('', 'temp\\one', [F])

```

