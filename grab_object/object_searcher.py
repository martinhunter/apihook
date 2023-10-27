import os
from typing import Dict


class HookTarget:
    def __init__(self, name, attrs=None, injection=None):
        self.name = name
        self.attrs = set(attrs) if attrs else set()
        self.injection = injection


class HookTargetManager:
    def __init__(self):
        self.data: Dict[str, HookTarget] = {}

    def add_one(self, target: HookTarget):
        name = target.name
        if name in self.data:
            self.data[name].attrs.update(target.attrs)
        else:
            self.data[name] = target

    def add_many(self, targets):
        for target in targets:
            self.add_one(target)

    def __iter__(self):
        return iter(self.data.values())


def parse_api(import_path, filters, mgr):
    module = __import__(import_path, fromlist=[''])
    for k, v in module.__dict__.items():
        if k.startswith('__'):
            continue
        name = import_path + '.' + k
        for f in filters:
            if isinstance(f, type):
                matched = f().filter(name, v)
            else:
                matched = f(name, v)
            if matched:
                mgr.add_one(matched)


def search_object(relative_path, module_path, filters):
    full_path = os.path.join(relative_path, module_path)
    module_path.replace('\\', '.').replace('/', '.')
    mgr = HookTargetManager()
    for file in os.listdir(full_path):
        if not file.endswith('.py'):
            continue
        import_path = '{}.{}'.format(module_path.replace('\\', '.').replace('/', '.'), file[:-3])
        parse_api(import_path, filters, mgr)
    return mgr

