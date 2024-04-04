import inspect
import os
import re
import sys
import types
from functools import wraps
from inspect import ismodule, isclass, isfunction, iscoroutinefunction
from typing import List, Any

from exceptions import HookEntryTypeErr
from injections import TestInjection

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


STATIC_METHOD = 'staticmethod'
CLASS_METHOD = 'classmethod'
INSTANCE_METHOD = 'instancemethod'


def reduce_arg(func_type):
    return func_type in [STATIC_METHOD, CLASS_METHOD]


def cls_func_type(func):
    if isinstance(func, staticmethod):
        return STATIC_METHOD
    elif isinstance(func, classmethod):
        return CLASS_METHOD
    elif isinstance(func, types.FunctionType):
        return INSTANCE_METHOD
    else:
        return None


def _hook_wrapper(target: Target, cls_name=''):
    def middle(func, func_type=None, counter=1):
        if cls_name:
            target.func_cls_map[func] = cls_name + '.'

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
                    if reduce_arg(func_type):
                        kls = args[0]
                        args = args[1:]
                    else:
                        kls = None
                    if target.injection_data is not None:
                        injection = injection_cls(func_name, kls, target.injection_data)
                    else:
                        injection = injection_cls(func_name, kls)
                    result = injection.start(*args, **kwargs)
                    if injection.skip_func:
                        return injection.end(result)
                    else:
                        result = await func(*args, **kwargs)
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
                    # if (not inspect.signature(func).parameters.get('self') and level == 2) or reduce_arg(func_type):
                    if counter == 1:
                        kls = args[0]
                        xargs = args
                    elif reduce_arg(func_type):
                        kls = args[0]
                        xargs = args[1:]
                    else:
                        xargs = args
                        kls = None
                    if target.injection_data is not None:
                        injection = injection_cls(func_name, kls, target.injection_data)
                    else:
                        injection = injection_cls(func_name, kls)
                    result = injection.start(*xargs, **kwargs)
                    if injection.skip_func:
                        return injection.end(result)
                    else:
                        if counter != 1:
                            result = func(*args, **kwargs)
                        else:
                            result = func(*xargs, **kwargs)
                        new_result = injection.end(result)
                        if injection.change_result:
                            return new_result
                        else:
                            return result
                else:
                    return func(*args, **kwargs)
        return inner

    return middle


def global_search_module_attr(attr_name, attr):
    # you have to replace attr with new_attr in all modules, so new_attr will make effect in all files
    for module_name, module_pack in sys.modules.items():
        if module_name.startswith('_'):
            continue
        for other_attr_name, other_attr in module_pack.__dict__.items():
            if other_attr_name == attr_name and other_attr == attr:
                yield module_pack


def get_inj_func_count(target: Target, the_func, func_name):
    full_name = '{}.{}'.format(target.target_name, func_name)
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


class ApiHooker(HookContextMixin):
    def __init__(self, target: Target):
        self.target = target
        self.original_attrs = []

    def hook_cls(self, cls):
        if self.target.includes:
            for func_name in self.target.get_func_names(cls):
                func = getattr(cls, func_name)
                the_func = cls.__dict__[func_name] if func_name in cls.__dict__ else func

                inj_counter = get_inj_func_count(self.target, the_func, func_name)
                wrapped_func = _hook_wrapper(self.target, cls_name=cls.__name__)(
                    func, inj_counter['func_type'], inj_counter['counter'])
                self.original_attrs.append([cls, func_name, the_func])
                setattr(cls, func_name, wrapped_func)
        else:
            cls_name = cls.__name__
            for module_pack in global_search_module_attr(cls_name, cls):
                self.original_attrs.append([module_pack, cls_name, cls])
                setattr(module_pack, cls_name, self.target.injection)

    def hook_func(self, module, func_name):
        func = getattr(module, func_name)
        if isclass(func):
            raise HookEntryTypeErr('{} is a class, not func in module {}'.format(func_name, module))
        for module_pack in global_search_module_attr(func_name, func):
            wrapped_func = _hook_wrapper(self.target)(func)
            self.original_attrs.append([module_pack, func_name, func])
            setattr(module_pack, func_name, wrapped_func)

    def hook_module(self, module):
        for func_name in self.target.get_func_names(module):
            self.hook_func(module, func_name)

    def start_hook(self):
        module, target = self.target.get_target()
        if ismodule(target):
            self.hook_module(target)
        elif isclass(target):
            self.hook_cls(target)
        elif isfunction(target):
            self.hook_func(module, target.__name__)
        else:
            raise HookEntryTypeErr('{} is not func, class, module'.format(target))

    def end_hook(self):
        # last in first out
        while self.original_attrs:
            pack, func_name, func = self.original_attrs.pop()
            setattr(pack, func_name, func)


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

    def start_hook(self):
        for hooker in self.hookers:
            hooker.start_hook()

    def end_hook(self):
        # last in first out
        for hooker in reversed(self.hookers):
            hooker.end_hook()


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
