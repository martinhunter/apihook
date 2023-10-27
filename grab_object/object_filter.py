from grab_object.object_searcher import HookTarget


class BaseObjectFilter:
    def filter(self, object_name, value):
        """
        :param object_name: name of object
        :param value: value of object
        :return: whether object will be hooked
        """
        return self.create(object_name)

    def create(self, name, attrs=None, injection=None):
        return HookTarget(name, attrs, injection)
