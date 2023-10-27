from grab_object import BaseObjectFilter
from hookers import condition_hookers


class ResourceFilter(BaseObjectFilter):
    pass


def flask_hookers(relative_path, module_path):
    filters = [ResourceFilter]
    return condition_hookers(relative_path, module_path, filters)
