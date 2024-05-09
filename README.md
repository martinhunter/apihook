# apihook
> dynamically hook/replace object globally.

## usable situations
1. run your program once and record params/results for unittest
2. run your program once and record params/results to mock api calls
3. run your program and replace 

## usage
e.g.
```python
from your_project import your_main_entry
import sys
sys.path.insert(0, r'D:\coding\pyprojects\mylibs')  # apihook在mylibs文件夹下
from api_hook import multi_hooker, LogInjectionBase, LogInjectionDataBase, api_hooker, BaseObjectFilter, condition_hookers
from api_hook.yaml_parser import yaml_dump_hookers
from api_hook.hookers import yaml_hookers
from api_hook.log_parser import get_log_data


HOOK_MODE = None


if HOOK_MODE == 'specify hook in code':
    hookers = multi_hooker()
    hookers.add_hook('your_project.part2.ExpClass', includes=['clsmethod2'], injection=LogInjectionBase)
    hookers.add_hook('your_project.part2.ExpClass', includes=['clsmethod2', 'func2', 'staticmethod2'])
    hookers.add_hook('your_project.part2', includes=['normal_func'])
    hookers.add_hook('your_project.part2.normal_func2')
    with hookers:  # function restored after exting scope
        your_main_entry()
elif HOOK_MODE == 'inject param/result from log':
    hookers = multi_hooker()
    common_hooker_1 = api_hooker('your_project.part3.ExpClass', includes=['func3'])
    hookers.add(common_hooker_1)
    hookers.add_hook('your_project.part2.ExpClass', includes=['clsmethod2'], injection=LogInjectionDataBase, 
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

## limits
1. hook class.member_method directly is not allowed.
    - Right!!! hookers.add_hook('your_project.part2.ExpClass', includes=['cls_method2', 'm_method2'])
    - Wrong!!! hookers.add_hook('your_project.part2.ExpClass.m_method2')    # raise exception
2. all hooks are at function level. Effect is global in your_project.
    1. effect ExpClass.func in all files
        - hookers.add_hook('your_project.part1.ExpClass', includes=['func'])  # setattr(ExpClass, func, wrapped(func))
        - unittest.mock.patch('your_project.part1.ExpClass.func')             # setattr(ExpClass, func, Mock1())
    2. effect only ExpClass directly used in current module(your_project.part2)
        - unittest.mock.patch('your_project.part2.ExpClass')                  # setattr(part2, ExpClass, Mock1())
    3. effect ExpClass, mo_func in all files
        - hookers.add_hook('your_project.part3.ExpClass')                     # for module_pack in sys.module; setattr(module_pack, ExpClass, MockExpClass)
        - hookers.add_hook('your_project.part3.mo_func')                      # for module_pack in sys.module; setattr(module_pack, mo_func, wrapped(mo_func))
3. replace object
    1. set replace to True in add_hook
        - hookers.add_hook('your_project.module_file.variable', injection='new_value', replace=True)
        - hookers.add_hook('your_project.module_file', includes=['func'], injection=new_func, replace=True)
        - hookers.add_hook('your_project.module_file.variable', injection='new_value')  # will raise error
4. can not hook the following types of code
    - classmethod/staticmethod that first param is its own class
        - For example:
            ```
            class SomeCls:
                @classmethod
                def compare(cls, other: SomeCls):
                    pass
                @staticmethod
                def compare2(other: SomeCls):
                    pass
            ```
        - Why: To fix the following situation, temp resolve is: `args=args[1:] if args and isinstance(args[0], SomeCls)`. So param "other" will be removed.
            ```
            some = SomeCls()
            some.cls_method(21)  # function's args is (<Some object at 0x04C6F328>, 21), this is unexpected param and will raise error
            SomeCls.cls_method(21)  # function's args is (21), this is expected param
            # Inside the hooked function, can not tell if it's instance call or class call.
            ```
            
            

