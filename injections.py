from loguru import logger


class InjectionBase:
    skip_func = False
    change_result = False

    def __init__(self, func):
        self.func = func

    def start(self, *args, **kwargs):
        self.hook_start(*args, **kwargs)

    def end(self, result):
        self.hook_end(result)

    def hook_start(self, *args, **kwargs):
        pass

    def hook_end(self, result):
        pass


class TestInjection(InjectionBase):
    def hook_start(self, *args, **kwargs):
        print('┌──────start──────┐')

    def hook_end(self, result):
        print('└───────end───────┘')


class LogInjectionBase(InjectionBase):
    file = 'log.log'

    def __init__(self, func):
        super().__init__(func)

    def start(self, *args, **kwargs):
        logger_id = logger.add(self.file)
        self.hook_start(*args, **kwargs)
        logger.remove(logger_id)

    def end(self, result):
        logger_id = logger.add(self.file)
        self.hook_end(result)
        logger.remove(logger_id)

    def hook_start(self, *args, **kwargs):
        msg = '{} {} {}'.format(self.func.__name__, *args, **kwargs)
        logger.info(msg)

    def hook_end(self, result):
        msg = '{} {}'.format(self.func.__name__, result)
        logger.info(msg)


class InjectionDataBase(InjectionBase):
    skip_func = True
    change_result = True

    def __init__(self, func, injection_data):
        super().__init__(func)
        assert injection_data is not None
        self.injection_data = injection_data
        self.matched = None

    @staticmethod
    def create_key(*args, **kwargs):
        return str(args) + str(kwargs)

    def start(self, *args, **kwargs):
        func = self.func.__name__  # TODO: 可能需要函数完整路径以避免不同模块的函数名重复
        if func in self.injection_data:
            key = self.create_key(*args, **kwargs)
            self.matched = self.injection_data[func].get(key, False)
        else:
            raise Exception('no matched data for func: {} args: {} {}'.format(func, args, kwargs))
        self.hook_start(*args, **kwargs)

    def end(self, result):
        # return new_result if hook_end returns value
        new_result = self.hook_end(result)
        if new_result is not None:
            return new_result
        return self.matched
