from loguru import logger


class InjectionBase:
    def __init__(self, func):
        self.func = func

    def start(self, *args, **kwargs):
        self.hook_start(*args, **kwargs)

    def end(self, result):
        self.hook_end(result)

    def hook_start(self, *args, **kwargs):
        raise NotImplemented

    def hook_end(self, result):
        raise NotImplemented


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
