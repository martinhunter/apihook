# apihook
> dynamically hook python functions params and results

## usable situations
1. run your program once and record params/results for unittest
2. run your program once and record params/results to mock api calls

## usage
e.g.
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

