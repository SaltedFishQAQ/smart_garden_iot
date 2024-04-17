
class BaseActuator(object):
    def __init__(self, name):
        self.name = name
        self.status = False

    def _on(self):
        pass

    def _off(self):
        pass

    def switch(self, set_on):
        self.status = set_on
        if set_on:
            self._on()
        else:
            self._off()

    def get_status(self):
        return "on" if self.status else "off"
