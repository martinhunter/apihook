from collections import OrderedDict

import yaml
import yamlloader

from hook_entry import multi_hooker


def _load_yaml(filename):
    with open(filename, mode='r', encoding='utf-8') as yaml_file:
        data = yaml.load(yaml_file, Loader=yamlloader.ordereddict.CLoader)
        return data


def _dump_yaml(data, filename):
    with open(filename, mode='w', encoding='utf-8') as yaml_file:
        data = yaml.dump(data, yaml_file, Dumper=yamlloader.ordereddict.CDumper)
        return data


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
        print(target, kwargs)
        if kwargs:
            hookers.add_hook(target=target, **kwargs)
        else:
            hookers.add_hook(target=target)
    return hookers


if __name__ == '__main__':
    print(yaml_hookers('example.yaml'))
