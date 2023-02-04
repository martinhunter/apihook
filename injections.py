from loguru import logger


class InjectionBase:
    trace_func = True  # trace which module called this func_name
    skip_func = False  # skip calling func_name
    change_result = False  # return result from hook_end

    def __init__(self, func_name):
        self.func_name = func_name

    def start(self, *args, **kwargs):
        self.hook_start(*args, **kwargs)

    def end(self, result):
        new_result = self.hook_end(result)
        if self.change_result:
            return new_result

    def hook_start(self, *args, **kwargs):
        pass  # pragma no cover

    def hook_end(self, result):
        pass  # pragma no cover


class TestInjection(InjectionBase):
    def hook_start(self, *args, **kwargs):
        print('┌──────start──────┐', self.func_name)

    def hook_end(self, result):
        print('└───────end───────┘')


class LogInjectionBase(InjectionBase):
    file = 'log.log'

    def __init__(self, func_name):
        super().__init__(func_name)

    def start(self, *args, **kwargs):
        logger_id = logger.add(self.file)
        self.hook_start(*args, **kwargs)
        logger.remove(logger_id)

    def end(self, result):
        logger_id = logger.add(self.file)
        self.hook_end(result)
        logger.remove(logger_id)

    def hook_start(self, *args, **kwargs):
        msg = '{} {} {}'.format(self.func_name, args, kwargs)
        logger.info(msg)

    def hook_end(self, result):
        msg = '{} {}'.format(self.func_name, result)
        logger.info(msg)


class InjectionDataBase(InjectionBase):
    skip_func = True  # do not change
    change_result = True  # do not change
    data_exception = True

    def __init__(self, func_name, injection_data):
        super().__init__(func_name)
        assert injection_data is not None
        self.injection_data = injection_data
        self.matched = None

    @staticmethod
    def create_key(*args, **kwargs):
        return str(args) + str(kwargs)

    def start(self, *args, **kwargs):
        func_name = self.func_name
        if func_name in self.injection_data:
            key = self.create_key(*args, **kwargs)
            self.matched = self.injection_data[func_name].get(key, False)
        else:
            if self.data_exception:
                raise Exception('no matched data for func_name: {} args: {} {}'.format(func_name, args, kwargs))
        self.hook_start(*args, **kwargs)

    def end(self, result):
        # return new_result if hook_end returns value else return self.matched
        new_result = self.hook_end(result)
        if new_result is not None:
            return new_result
        return self.matched


class InjectionDataNoException(InjectionDataBase):
    data_exception = False
