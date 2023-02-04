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


class YamlNode:
    def __init__(self, target='', attrs=None):
        self.target = target
        self.attrs = attrs
        self.child_nodes = []

    def __iter__(self):
        return iter(self.child_nodes)

    def add_child(self, node):
        self.child_nodes.append(node)

    @property
    def is_end(self):
        return not self.child_nodes


class YamlTree:
    def __init__(self):
        self.root = None

    def parse_data(self, hook_project_data):
        def recurse(data, node: YamlNode):
            if isinstance(data, OrderedDict):
                data = [data]
            for item in data:
                target = item.get('target', '')
                attrs = item.get('attrs')
                ns = item.get('ns')
                child_node = YamlNode(target, attrs)
                node.add_child(child_node)
                if ns:
                    recurse(ns, child_node)

        self.root = YamlNode()
        items = hook_project_data['ns']
        recurse(items, self.root)

    def _recurse_parsed_data(self):
        def recurse_node(node: YamlNode, target=''):
            for child_node in node:
                child_target = child_node.target
                if target:
                    new_target = target + '.' + child_target
                else:
                    new_target = child_target
                if child_node.attrs or child_node.is_end:
                    if not child_target:
                        raise Exception('target not exist in ns: {} for attrs: {}'.format(target, child_node.attrs))
                    yield {'target': new_target, 'attrs': child_node.attrs}
                if not child_node.is_end:
                    yield from recurse_node(child_node, new_target)

        yield from recurse_node(self.root)

    def __iter__(self):
        return iter(self._recurse_parsed_data())


def tree_parse_yaml(filename):
    loaded = _load_yaml(filename)
    for k, v in loaded.items():
        if k == 'hook_project':
            tree = YamlTree()
            tree.parse_data(v)
            return tree


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
