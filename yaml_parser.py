from collections import OrderedDict

import yaml
import yamlloader


def _load_yaml(filename):
    with open(filename, mode='r', encoding='utf-8') as yaml_file:
        data = yaml.load(yaml_file, Loader=yamlloader.ordereddict.CLoader)
        return data


def _dump_yaml(data, filename):
    with open(filename, mode='w', encoding='utf-8') as yaml_file:
        data = yaml.dump(data, yaml_file, Dumper=yamlloader.ordereddict.CDumper)
        return data


def recursive_parse(data, container, prefix=''):
    if isinstance(data, OrderedDict):
        data = [data]
    print(data)
    for item in data:
        new_prefix = prefix
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
            container.append({'target': new_prefix, 'attrs': attrs})
        if ns:
            recursive_parse(ns, container, new_prefix)


def parse_yaml(filename):
    loaded = _load_yaml(filename)
    projects = {}
    for k, v in loaded.items():
        container = []
        projects[k] = recursive_parse(v, container)
        for item in container:
            print(item)

    return projects

if __name__ == '__main__':
    parse_yaml('example.yaml')
