from biz.base_device import BaseDevice
import time


class DemoDevice(BaseDevice):
    def __init__(self, name):
        super().__init__(name, "mqtt.eclipseprojects.io", 1883)

    def handle_message(self, client, userdata, msg):
        print("current device:", self.device_name)
        print(f"received {msg.payload.decode('utf-8')} under topic {msg.topic}")


if __name__ == '__main__':
    device = DemoDevice("device1")
    device.init_mqtt_client()
    device.mqtt_listen("iot/lwx123321/test1", device.handle_message)

    device2 = DemoDevice("device2")
    device2.init_mqtt_client()
    device2.mqtt_publish("iot/lwx123321/test1", "this is a message")

    while True:
        time.sleep(10)

