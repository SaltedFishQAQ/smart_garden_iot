import message_broker.channels as mb_channel


class BaseActuator(object):
    def __init__(self, name):
        self.name = name
        self.status = False
        self.operation_topic = mb_channel.DEVICE_OPERATION

    def _on(self):
        pass

    def _off(self):
        pass

    def switch(self, set_on):
        self.status = set_on
        if set_on:
            return self._on()
        else:
            return self._off()

    def display_status(self):
        return "on" if self.status else "off"
