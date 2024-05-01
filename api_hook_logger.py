import logging
import os


def create_logger(name, folder=None, level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    log_file_path = os.path.join(folder or os.path.dirname(__file__), '{}.log'.format(name))
    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(funcName)s:%(lineno)d|| %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


hook_log = create_logger('hook_log')
