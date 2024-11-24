import threading
import time
from typing import Callable, final


class BaseSensor(object):
    def __init__(self, name):
        self.name = name
        self.running = False
        self.lock = False
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

    def measurement(self) -> str:
        pass

    @final
    def _thread_main(self):
        if self.lock:
            return
        self.lock = True

        while self.running:
            for _ in range(30):
                time.sleep(10)
                if self.running is False:
                    self.lock = False
                    return
            self.receiver(self.monitor())

    @property
    def receiver(self):
        return self._receiver

    @receiver.setter
    def receiver(self, func: Callable[[str], None]):
        self._receiver = func


def mock_receiver(data: str):
    print(f'sensor gets data: {data}')
