import copy
import inspect
import re
from functools import wraps
from inspect import signature, ismodule, isclass, isfunction, iscoroutinefunction
from typing import List, Any

from injections import TestInjection, InjectionDataBase


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
        module = None  # get namespace if unnecessary
        attr = target
    else:
        raise Exception('target type {} is not acceptable'.format(type(target)))
    return module, attr


class HookContextMixin:
    def start_hook(self):
        raise NotImplemented

    def end_hook(self):
        raise NotImplemented

    def __enter__(self):
        self.start_hook()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_hook()


class Target:
    def __init__(self, target: Any, includes: List[str] = None, exclude_regex: str = '_.*',
                 injection=TestInjection, injection_data=None):
        self.target = target
        self.includes = includes
        self.exclude_regex = re.compile(exclude_regex)
        self.injection = self.parse_injection(injection)
        self.injection_data = injection_data
        self.func_cls_map = {}

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
            func_names = [func_name for func_name in cls.__dict__ if not self.exclude_regex.match(func_name)]
        return func_names

    def get_target(self):
        return _get_target_by_type(self.target)


import os

_cwd = os.getcwd()


def _hook_wrapper(target: Target, cls_name=''):
    def middle(func):
        if cls_name:
            target.func_cls_map[func] = cls_name + '.'

        def parse_trace_func(func_call, trace_func=True):
            if not trace_func:
                return func_call.__name__
            # trace which file called this func
            frame = inspect.currentframe()
            while frame:
                caller_file = frame.f_code.co_filename
                if caller_file.endswith('hook_entry.py'):
                    frame = frame.f_back
                else:
                    return target.get_trace_func(func_call, caller_file)

        if iscoroutinefunction(func):
            @wraps(func)
            async def inner(*args, **kwargs):
                if cls_name and not signature(func).parameters.get('self'):  # 修正classmethod和staticmethod
                    args = args[1:]  # TODO: 复制行为是否会出错？
                injection_cls = target.injection
                if injection_cls:
                    func_name = parse_trace_func(func, injection_cls.trace_func)
                    if issubclass(injection_cls, InjectionDataBase):
                        injection = injection_cls(func_name, target.injection_data)
                    else:
                        injection = injection_cls(func_name)
                    injection.start(*args, **kwargs)
                    if injection.skip_func:
                        return injection.end(None)
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
                if cls_name and not signature(func).parameters.get('self'):  # 修正classmethod和staticmethod
                    args = args[1:]  # TODO: 复制行为是否会出错？
                injection_cls = target.injection
                if injection_cls:
                    func_name = parse_trace_func(func, injection_cls.trace_func)
                    if issubclass(injection_cls, InjectionDataBase):
                        injection = injection_cls(func_name, target.injection_data)
                    else:
                        injection = injection_cls(func_name)
                    injection.start(*args, **kwargs)
                    if injection.skip_func:
                        return injection.end(None)
                    else:
                        result = func(*args, **kwargs)
                        new_result = injection.end(result)
                        if injection.change_result:
                            return new_result
                        else:
                            return result
                else:
                    return func(*args, **kwargs)

        return inner

    return middle


class ApiHooker(HookContextMixin):
    def __init__(self, target: Target):
        self.target = target
        self.original_attrs = []

    def hook_cls(self, cls):
        for func_name in self.target.get_func_names(cls):
            func = getattr(cls, func_name)
            wrapped_func = _hook_wrapper(self.target, cls_name=cls.__name__)(func)
            self.original_attrs.append([cls, func_name, cls.__dict__[func_name]])
            setattr(cls, func_name, wrapped_func)

    def hook_func(self, module, func_name):
        func = getattr(module, func_name)
        if isclass(func):
            raise Exception('{} is a class, not func in module {}'.format(func_name, module))
        import sys
        for module_name, module_pack in sys.modules.items():
            if module_name.startswith('_'):
                continue
            for other_func_name, other_func in module_pack.__dict__.items():
                if other_func_name == func_name and other_func == func:
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
            raise Exception('{} is not func, class, module'.format(target))

    def end_hook(self):
        # last in first out
        while self.original_attrs:
            pack, func_name, func = self.original_attrs.pop()
            setattr(pack, func_name, func)


class ApiHookers(HookContextMixin):
    def __init__(self, hookers: List[ApiHooker] = None):
        self.hookers = hookers or []

    def add_hook(self, target: Any, includes: List[str] = None, exclude_regex: str = '_.*',
                 injection=TestInjection, injection_data=None):
        self.hookers.append(api_hooker(target, includes, exclude_regex, injection))

    def add(self, hooker: ApiHooker):
        self.hookers.append(copy.copy(hooker))

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
    :return: hooker object
    """
    target_object = Target(target, includes, exclude_regex, injection, injection_data)
    return ApiHooker(target_object)


def multi_hooker(hookers: List[ApiHooker] = None):
    return ApiHookers(hookers)
