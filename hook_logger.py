import logging
import os

from conf import DEBUG_API_HOOK


def create_logger(name, level=logging.DEBUG, folder=None):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    log_file_path = os.path.join(folder or os.path.dirname(__file__), '{}.log'.format(name))
    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - (%(threadName)s):%(filename)s:%(funcName)s:%('
                                  'lineno)d - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


hook_log = create_logger('hook_log', level=DEBUG_API_HOOK)
