import threading
import time
from typing import Callable, final


class BaseSensor(object):
    def __init__(self, name):
        self.name = name
        self.running = False
        self._receiver = mock_receiver

    @final
    def start(self):
        self.running = True
        threading.Thread(target=self._thread_main).start()

    @final
    def stop(self):
        self.running = False

    def monitor(self) -> str:
        pass

    @final
    def _thread_main(self):
        while self.running:
            self.receiver(self.monitor())
            time.sleep(60*10)

    @property
    def receiver(self):
        return self._receiver

    @receiver.setter
    def receiver(self, func: Callable[[str], None]):
        self._receiver = func


def mock_receiver(data: str):
    print(f'sensor gets data: {data}')
