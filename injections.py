import hashlib

from loguru import logger


class ReplaceBase:
    pass


class InjectionBase:
    skip_func = False  # skip calling func_name
    change_result = False  # return result from hook_end

    def __init__(self, func_name, func_type):
        self.func_name = func_name
        self.func_type = func_type
        self.ins = None

    def start(self, *args, **kwargs):
        return self.hook_start(*args, **kwargs)

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


class InjSkip(InjectionBase):
    skip_func = True


class InjChange(InjectionBase):
    change_result = True

    def hook_end(self, result):
        return result


class InjChangeSkip(InjChange):
    skip_func = True

    def hook_start(self, *args, **kwargs):
        print(args, kwargs)


def md5_params(*args, **kwargs):
    m = hashlib.md5()
    m.update(str(args).encode('utf-8'))
    m.update(str(sorted(kwargs.items())).encode('utf-8'))
    return m.hexdigest()


class LogInjectionBase(InjectionBase):
    file = 'log.log'

    def start(self, *args, **kwargs):
        self.arg = md5_params(*args, **kwargs)
        self.hook_start(*args, **kwargs)

    def end(self, result):
        msg = '{} {} {}'.format(self.func_name, self.arg, result)  # record original result
        logger_id = logger.add(self.file)
        logger.info(msg)
        logger.remove(logger_id)
        self.hook_end(result)


class InjectionDataBase(InjChange):
    change_result = True  # do not modify
    data_exception = True

    def __init__(self, func_name, func_type, inj_data=None):
        super().__init__(func_name, func_type)
        self.injection_data = inj_data
        self.matched = None

    @staticmethod
    def create_key(*args, **kwargs):
        return str(args) + str(kwargs)

    def start(self, *args, **kwargs):
        func_name = self.func_name
        if func_name in self.injection_data:
            key = md5_params(*args, **kwargs)
            self.matched = self.injection_data[func_name].get(key)
        else:
            if self.data_exception:
                raise Exception('no matched data for func_name: {} args: {} {}'.format(func_name, args, kwargs))
        return self.hook_start(*args, **kwargs)

    def end(self, result):
        # return new_result if hook_end returns value else return self.matched
        new_result = self.hook_end(result)
        if new_result is not None:
            return new_result
        return self.matched


class InjectionDataNoException(InjectionDataBase):
    data_exception = False


class RepCeleryTask:
    @staticmethod
    def apply_async(args=None, kwargs=None, task_id=None, producer=None,
                    link=None, link_error=None, shadow=None, **options):
        pass
