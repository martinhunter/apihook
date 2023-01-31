class InjectionBase:
    def __init__(self, func):
        self.func = func

    def hook_start(self, *args, **kwargs):
        raise NotImplemented

    def hook_end(self, result):
        raise NotImplemented


class TestInjection(InjectionBase):
    def hook_start(self, *args, **kwargs):
        print('┌──────start──────┐')

    def hook_end(self, result):
        print('└───────end───────┘')
