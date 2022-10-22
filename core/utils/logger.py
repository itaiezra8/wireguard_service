import logging
import sys


class Logger:
    def __init__(self, service: str):
        self.service = service

    def get_logger(self):
        my_logger = logging.getLogger()
        my_logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(f'%(asctime)s | %(levelname)s | {self.service} | %(message)s')

        sh = logging.StreamHandler(sys.stdout)
        sh.setLevel(logging.INFO)
        sh.setFormatter(formatter)

        fh = logging.FileHandler('logs.log')
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)

        my_logger.addHandler(fh)
        my_logger.addHandler(sh)
        return my_logger
