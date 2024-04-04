import types

STATIC_METHOD = 'staticmethod'
CLASS_METHOD = 'classmethod'
INSTANCE_METHOD = 'instancemethod'


def reduce_arg(func_type):
    return func_type in [STATIC_METHOD, CLASS_METHOD]


def is_cls_func(func_type):
    return func_type in [STATIC_METHOD, CLASS_METHOD, INSTANCE_METHOD]


def cls_func_type(func):
    if isinstance(func, staticmethod):
        return STATIC_METHOD
    elif isinstance(func, classmethod):
        return CLASS_METHOD
    elif isinstance(func, types.FunctionType):
        return INSTANCE_METHOD
    else:
        return None