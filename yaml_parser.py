from collections import OrderedDict
from typing import Union

import yaml
import yamlloader

from hook_entry import multi_hooker, Target, ApiHooker, ApiHookers, get_target_name


def _load_yaml(filename):
    with open(filename, mode='r', encoding='utf-8') as yaml_file:
        data = yaml.load(yaml_file, Loader=yamlloader.ordereddict.CLoader)
        return data


def _dump_yaml(data, filename):
    with open(filename, mode='w', encoding='utf-8') as yaml_file:
        data = yaml.dump(data, yaml_file, Dumper=yamlloader.ordereddict.CDumper)
        return data


def _create_yaml_attrs(target: Target):
    di = OrderedDict()
    if target.includes:
        di['includes'] = target.includes
    if target.injection:
        di['injection'] = get_target_name(target.injection)
    if target.exclude_regex:
        di['exclude_regex'] = target.exclude_regex.pattern
    return di


def _merge_target(hookers):
    def recurse(target_names, parent):
        target, targets_list = target_names
        if target:
            parent['target'] = target
        parent['ns'] = []

        di = OrderedDict()
        for target_name, target_object in targets_list:
            li = target_name.split('.', maxsplit=1)
            if len(li) == 1:
                obj = OrderedDict()
                obj['target'] = li[0]
                obj['attrs'] = _create_yaml_attrs(target_object)
                parent['ns'].append(obj)
            else:
                ns, rest = li
                if ns not in di:
                    di[ns] = []
                di[ns].append([rest, target_object])
        for ns, v in di.items():
            for item in parent['ns']:
                if item.get('target') == ns:
                    obj = item
                    break
            else:
                obj = OrderedDict()
                parent['ns'].append(obj)
            recurse([ns, v], obj)

    container = OrderedDict()
    targets = ["", [[hooker.target.target_name, hooker.target] for hooker in hookers]]
    recurse(targets, container)
    return OrderedDict({"hook_project": container})


def yaml_dump_hookers(hookers: Union[ApiHookers, ApiHooker], file):
    if isinstance(hookers, ApiHookers):
        hookers = hookers.hookers
    else:
        hookers = [hookers]
    yaml_dict = _merge_target(hookers)
    _dump_yaml(yaml_dict, file)


def _recursive_parse(data, prefix=''):
    if isinstance(data, OrderedDict):
        data = [data]
    for item in data:
        new_prefix = prefix  # copy to avoid modify shared variable in loops
        attrs = item.get('attrs')
        target = item.get('target')
        ns = item.get('ns')

        if target:
            if new_prefix:
                new_prefix += '.' + target
            else:
                new_prefix = target
        if attrs or not ns:
            if not target:
                raise Exception('target not exist in ns: {} for attrs: {}'.format(new_prefix, attrs))
            yield {'target': new_prefix, 'attrs': attrs}
        if ns:
            yield from _recursive_parse(ns, new_prefix)


def parse_yaml(filename):
    loaded = _load_yaml(filename)
    for k, v in loaded.items():
        if k == 'hook_project':
            return _recursive_parse(v)


def yaml_hookers(filename):
    """
    yaml ns list order matters if you want to apply multiple injection on the same function
    e.g.
    ns:
      - target: Part2
        attrs:
          includes:
            - cls2
      - target: Part2
        attrs:
          includes:
          - cls2
          - func2
          - sta2
    :param filename:
    :return:
    """
    hookers = multi_hooker()
    for item in parse_yaml(filename):
        target: str = item['target']
        kwargs: dict = item['attrs']
        if kwargs:
            hookers.add_hook(target=target, **kwargs)
        else:
            hookers.add_hook(target=target)
    return hookers
