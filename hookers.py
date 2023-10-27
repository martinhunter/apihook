from grab_object import search_object
from hook_entry import multi_hooker
from yaml_parser import parse_yaml


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


def condition_hookers(relative_path, module_path, filters: list):
    """
    :param relative_path: source root directory
    :param module_path: folder of .py files
    :param filters: hook all matched class/functions
    :return:
    """
    hookers = multi_hooker()
    targets = search_object(relative_path, module_path, filters)
    for target in targets:
        hookers.add_hook(target.name, include_attrs=target.attrs, injection=target.injection)
    return hookers
