from loguru import logger


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


class LogInjectionBase(InjectionBase):
    file = 'log.log'

    def __init__(self, func):
        super().__init__(func)
        self.logger = logger.add(self.file)

    def hook_start(self, *args, **kwargs):
        msg = '{} {} {}'.format(self.func.__name__, *args, **kwargs)
        logger.info(msg)

    def hook_end(self, result):
        msg = '{} {}'.format(self.func.__name__, result)
        logger.info(msg)
        logger.remove(self.logger)
