from datetime import datetime
from common.time import time_to_str


LEVEL_INFO = "info"
LEVEL_WARNING = "Warning!"
LEVEL_ERROR = "Error!!!"


class Logger:
    def __init__(self, prefix=""):
        self.prefix = prefix

    def _print(self, level, msg):
        now = time_to_str(datetime.now())
        print(f'[{level}] "{now}" - {self.prefix} {msg}')

    def info(self, msg):
        self._print(LEVEL_INFO, msg)

    def warning(self, msg):
        self._print(LEVEL_WARNING, msg)

    def error(self, err):
        self._print(LEVEL_ERROR, err)
