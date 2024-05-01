import inspect
import os
import re
import sys
from collections import defaultdict
from functools import wraps
from inspect import ismodule, isclass, isfunction, iscoroutinefunction
from typing import List, Any

from common import reduce_arg, cls_func_type
from conf import *
from exceptions import HookEntryTypeErr, BadConfiguration
from hook_logger import hook_log
from injections import TestInjection

_hooked_global = []


def _check_hooked_global(the_module, the_attr):
    if INJECTION_LEVEL == INJECTION_LEVEL_GLOBAL:
        for layer in _hooked_global:
            for h in layer:
                for module, attr, _ in h.original_attrs:
                    if the_module == module and the_attr == attr:
                        return False
        return True
    elif INJECTION_LEVEL == INJECTION_LEVEL_MULTI:
        for layer in _hooked_global[:-1]:
            for h in layer:
                for module, attr, _ in h.original_attrs:
                    if the_module == module and the_attr == attr:
                        return False
        return True
    elif INJECTION_LEVEL == INJECTION_LEVEL_SINGLE:
        return True
    else:
        raise BadConfiguration('injection level:%s not supported'.format(INJECTION_LEVEL))


_cwd = os.getcwd()


def _dot_lookup(thing, comp, import_path):
    try:
        return getattr(thing, comp)
    except AttributeError:
        __import__(import_path)
        return getattr(thing, comp)


def _importer(target):
    components = target.split('.')
    import_path = components.pop(0)
    thing = __import__(import_path)

    for comp in components:
        import_path += ".%s" % comp
        thing = _dot_lookup(thing, comp, import_path)
    return thing


def _get_target(target):
    # copied from unittest.mock.patch
    try:
        target, attribute = target.rsplit('.', 1)
    except (TypeError, ValueError, AttributeError):
        raise TypeError(
            f"Need a valid target to patch. You supplied: {target!r}")
    getter = lambda: _importer(target)
    return getter, attribute


def _get_attr(target):
    getter, cls_module_name = _get_target(target)
    module = getter()
    return getattr(module, cls_module_name)


def _get_target_by_type(target):
    if isinstance(target, str):
        getter, cls_module_name = _get_target(target)
        module = getter()
        attr = getattr(module, cls_module_name)
    elif isclass(target) or isfunction(target):
        import sys
        module = sys.modules[target.__module__]
        attr = target
    elif ismodule(target):
        module = None  # get module namespace is unnecessary
        attr = target
    else:
        raise HookEntryTypeErr('target type {} is not acceptable'.format(type(target)))
    return module, attr


def get_target_name(name):
    if isinstance(name, str):
        target_name = name
    else:
        module, target = _get_target_by_type(name)
        if ismodule(target):
            target_name = target.__name__
        else:
            target_name = module.__name__ + '.' + target.__name__
    return target_name


func_inj_counter = {}


class HookContextMixin:
    def start_hook(self):
        raise NotImplemented  # pragma no cover

    def end_hook(self):
        raise NotImplemented  # pragma no cover

    def __enter__(self):
        self.start_hook()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_hook()


class Target:
    def __init__(self, name: Any, includes: List[str] = None, exclude_regex: str = '_.*',
                 injection=TestInjection, injection_data=None):
        self.name = name
        self.includes = includes
        self.exclude_regex = re.compile(exclude_regex)
        self.injection = self.parse_injection(injection)
        self.injection_data = injection_data
        self.func_cls_map = {}

    @property
    def target_name(self):
        return get_target_name(self.name)

    def get_trace_func(self, func, caller_file):
        file = caller_file.replace(_cwd, '').replace('/', '.').replace('\\', '.')[1:-2]
        func_name = self.func_cls_map.get(func, '') + func.__name__
        return file + func_name

    @staticmethod
    def parse_injection(injection):
        if isinstance(injection, str):
            return _get_attr(injection)
        return injection

    def get_func_names(self, cls):
        if self.includes:
            func_names = self.includes
        else:
            if ismodule(cls):
                print("WARNING: only functions in module will be hooked")
                func_names = [func_name for func_name in cls.__dict__ if
                              not self.exclude_regex.match(func_name) and isfunction(getattr(cls, func_name))]
            else:
                func_names = [func_name for func_name in cls.__dict__ if not self.exclude_regex.match(func_name)]
        return func_names

    def get_target(self):
        return _get_target_by_type(self.name)

    def get_variable(self):
        getter, cls_module_name = _get_target(self.name)
        module = getter()
        return module, cls_module_name


def _hook_wrapper(target: Target, cls=''):
    def middle(func, func_type=None, counter=1):
        if cls:
            target.func_cls_map[func] = cls.__name__ + '.'

        def parse_trace_func(func_call):
            # trace which file called this func
            frame = inspect.currentframe()
            counter = 0
            while frame:
                caller_file = frame.f_code.co_filename
                if caller_file.endswith('hook_entry.py'):
                    counter += 1
                    frame = frame.f_back
                else:
                    return target.get_trace_func(func_call, caller_file), counter

        if iscoroutinefunction(func):
            @wraps(func)
            async def inner(*args, **kwargs):
                injection_cls = target.injection
                if injection_cls:
                    func_name, level = parse_trace_func(func)
                    if target.injection_data is not None:
                        injection = injection_cls(func_name, func_type, target.injection_data)
                    else:
                        injection = injection_cls(func_name, func_type)

                    if counter == 1 and reduce_arg(func_type) and (args and isinstance(args[0], cls)):
                        # fix classmethod and staticmethod
                        new_args = args[1:]
                    else:
                        new_args = args
                    result = injection.start(new_args, **kwargs)
                    if injection.skip_func:
                        return injection.end(result)
                    else:
                        result = await func(*new_args, **kwargs)
                        new_result = injection.end(result)
                        if injection.change_result:
                            return new_result
                        else:
                            return result
                else:
                    return await func(*args, **kwargs)
        else:
            @wraps(func)
            def inner(*args, **kwargs):
                injection_cls = target.injection
                if injection_cls:
                    func_name, level = parse_trace_func(func)
                    if target.injection_data is not None:
                        injection = injection_cls(func_name, func_type, target.injection_data)
                    else:
                        injection = injection_cls(func_name, func_type)
                    if cls:
                        if reduce_arg(func_type) and not (args and isinstance(args[0], cls)):
                            # fix classmethod and staticmethod
                            injection.ins = cls
                            new_args = args
                        else:
                            injection.ins = args[0]
                            new_args = args[1:]
                    else:
                        new_args = args
                    result = injection.start(*new_args, **kwargs)
                    if injection.skip_func:
                        return injection.end(result)
                    else:
                        if cls and counter == 1 and reduce_arg(func_type) and (args and isinstance(args[0], cls)):
                            # fix classmethod and staticmethod
                            new_args = args[1:]
                        else:
                            new_args = args
                        result = func(*new_args, **kwargs)
                        new_result = injection.end(result)
                        if injection.change_result:
                            return new_result
                        else:
                            return result
                else:
                    return func(*args, **kwargs)
        return inner

    return middle


def global_search_module_attr(attr_name, attr, project_module_name=None):
    # you have to replace attr with new_attr in all modules, so new_attr will make effect in all files
    for module_name, module_pack in sys.modules.items():
        if module_name.startswith('_'):
            continue
        if project_module_name and not module_name.startswith(project_module_name):
            # only your project will be effected
            continue
        for other_attr_name, other_attr in module_pack.__dict__.items():
            if other_attr_name == attr_name == 'part2_normal':
                print('-----', module_pack, other_attr, attr)
            if other_attr_name == attr_name and other_attr == attr:
                yield module_pack


def get_full_func_name(target: Target, func_name: str):
    full_name = '{}.{}'.format(target.target_name, func_name)
    return full_name


def get_inj_func_count(full_name, the_func):
    """
    staticmethod, classmethod will be turned into function if injected multiple times,
    staticmethod, classmethod, function parameters have to be handled differently.
    so counter is required to distinguish.
    :param target:
    :param the_func:
    :param func_name:
    :return: func_type and its counter
    """

    if full_name in func_inj_counter:
        item = func_inj_counter[full_name]
        item['counter'] += 1
    else:
        counter = 1
        func_type = cls_func_type(the_func)
        func_inj_counter[full_name] = {
            'counter': counter,
            'func_type': func_type
        }
    return func_inj_counter[full_name]


def get_project_module_name(module, level=1):
    if module:
        li = module.__name__.split('.')
        project_module_name = '.'.join(li[:min(len(li), level)])
    else:
        project_module_name = None
    return project_module_name


class ApiHooker(HookContextMixin):
    def __init__(self, target: Target):
        self.target = target
        self.original_attrs = []
        self.replaced_attrs = []
        self.inj_counter = defaultdict(int)

    def set_hook(self, the_module, the_attr, original_value, new_value):
        if _check_hooked_global(the_module, the_attr):
            self.original_attrs.append([the_module, the_attr, original_value])
            self.replaced_attrs.append([the_module, the_attr, new_value])
            setattr(the_module, the_attr, new_value)
            hook_log.info('HOOKED module:{} attr:{} value:{}'.format(the_module, the_attr, new_value))
        else:
            hook_log.warning('NOT HOOK module:{} attr:{} value:{}'.format(the_module, the_attr, original_value))

    def hook_cls(self, cls, module):
        if self.target.includes:
            # cls is not changed, funcs of cls will be hooked
            for func_name in self.target.get_func_names(cls):
                func = getattr(cls, func_name)
                the_func = cls.__dict__[func_name] if func_name in cls.__dict__ else func

                full_name = get_full_func_name(self.target, func_name)
                inj_counter = get_inj_func_count(full_name, the_func)
                wrapped_func = _hook_wrapper(self.target, cls=cls)(
                    func, inj_counter['func_type'], inj_counter['counter'])
                self.inj_counter[full_name] += 1
                self.set_hook(cls, func_name, the_func, wrapped_func)
        else:
            # cls need to be hooked in all modules
            cls_name = cls.__name__
            for module_pack in global_search_module_attr(cls_name, cls, get_project_module_name(module)):
                self.set_hook(module_pack, cls_name, cls, self.target.injection)

    def hook_func(self, module, func_name):
        # func need to be hooked in all modules
        func = getattr(module, func_name)
        if isclass(func):
            raise HookEntryTypeErr('{} is a class, not func in module {}'.format(func_name, module))
        for module_pack in global_search_module_attr(func_name, func, get_project_module_name(module)):
            wrapped_func = _hook_wrapper(self.target)(func)
            self.set_hook(module_pack, func_name, func, wrapped_func)

    def hook_module(self, module):
        for func_name in self.target.get_func_names(module):
            self.hook_func(module, func_name)

    def hook_variable(self):
        # variables need to be hooked in all modules
        module, attr_name = self.target.get_variable()
        value = getattr(module, attr_name)
        for module_pack in global_search_module_attr(attr_name, value, get_project_module_name(module)):
            self.set_hook(module_pack, attr_name, value, self.target.injection)

    def start_hook(self):
        module, target = self.target.get_target()
        if ismodule(target):
            # module is None
            self.hook_module(target)
        elif isclass(target):
            self.hook_cls(target, module)
        elif isfunction(target):
            self.hook_func(module, target.__name__)
        else:
            print('WARNING: {} is not func, class, module'.format(target))
            if callable(target):
                self.hook_cls(target, module)
            else:
                self.hook_variable()

    def end_hook(self):
        # last in first out
        while self.original_attrs:
            pack, func_name, func = self.original_attrs.pop()
            setattr(pack, func_name, func)
        self.replaced_attrs = []
        for full_name, counter in self.inj_counter.items():
            func_inj_counter[full_name]['counter'] -= counter


class ApiHookers(HookContextMixin):
    def __init__(self, hookers: List[ApiHooker] = None):
        self.hookers = hookers or []

    def __iter__(self):
        return iter(self.hookers)

    def add_hook(self, target: Any, includes: List[str] = None, exclude_regex: str = '_.*',
                 injection=TestInjection, injection_data=None):
        self.hookers.append(api_hooker(target, includes, exclude_regex, injection, injection_data))

    def add(self, hooker: ApiHooker):
        self.hookers.append(hooker)

    def rm_hook(self, hooker: ApiHooker):
        self.hookers.remove(hooker)

    @staticmethod
    def _log_hooked_details(action):
        if _hooked_global:
            hook_log.info("CURRENTLY HOOKED AFTER {}".format(action))
        else:
            hook_log.info("NOTHING CURRENTLY HOOKED AFTER {}".format(action))
        for idx, layer in enumerate(_hooked_global):
            if layer:
                hook_log.info("__layer {} hooks".format(idx))
            else:
                hook_log.info("__layer {} hooks empty".format(idx))
            for h in layer:
                for module, attr, value in h.replaced_attrs:
                    hook_log.info("__module:{} attr:{} value:{}".format(module, attr, value))

    def start_hook(self):
        hook_log.info("START: layer {} multi hook".format(len(_hooked_global)))
        _hooked_global.append(self.hookers)
        for hooker in self.hookers:
            hooker.start_hook()
        self._log_hooked_details('__ENTER__')

    def end_hook(self):
        # last in first out
        for hooker in reversed(self.hookers):
            hooker.end_hook()
        _hooked_global.pop()
        self._log_hooked_details('__EXIT__')
        hook_log.info("END: layer {} multi hook".format(len(_hooked_global)))


def api_hooker(target: Any, includes: List[str] = None, exclude_regex: str = '_.*',
               injection=TestInjection, injection_data=None):
    """
    hook specified functions
    :param target: the module/cls to be hooked
    :param includes: funcs of module/cls to be hooked
    :param exclude_regex: matched funcs will not be hooked
    :param injection: your hook class
    :param injection_data: data to insert into hook class
    :return: hooker object
    """
    target_object = Target(target, includes, exclude_regex, injection, injection_data)
    return ApiHooker(target_object)


def multi_hooker(hookers: List[ApiHooker] = None):
    return ApiHookers(hookers)
