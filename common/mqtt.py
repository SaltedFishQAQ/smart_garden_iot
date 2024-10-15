import paho.mqtt.client as mqtt_client


class MQTTClient:
    def __init__(self, client_id, broker, port):
        self.broker = broker
        self.port = port
        self.client_id = client_id
        self.is_subscriber = False
        self.topics = []
        self.topic_handlers = {}

        # init mqtt client
        self.client = mqtt_client.Client(client_id, False)
        # register callback functions
        self.client.on_connect = self.handle_connect
        self.client.on_message = self.handle_message

    def start(self):
        self.client.connect(self.broker, self.port, keepalive=60)
        self.client.reconnect_delay_set(min_delay=1, max_delay=120)
        self.client.loop_start()

    def stop(self):
        if self.is_subscriber:
            for topic in self.topics:
                self.client.unsubscribe(topic)
        self.is_subscriber = False
        self.topics = []

        self.client.loop_stop()
        self.client.disconnect()

    def publish(self, topic, msg):
        self.client.publish(topic, msg)

    def subscribe(self, topic, handler):
        self.is_subscriber = True
        self.topics.append(topic)
        self.topic_handlers[topic] = handler

        self.client.subscribe(topic, 2)

    def handle_connect(self, client, userdata, flags, rc):
        pass
    
    def handle_message(self, client, userdata, msg):
        match_list = self._topic_match(msg.topic)
        if len(match_list) == 0:
            print(f"topic {msg.topic} no match callback")
            return

        for register_topic in match_list:
            self.topic_handlers[register_topic](client, userdata, msg)

    def _topic_match(self, curr_topic):
        match_list = []
        for register_topic in self.topic_handlers.keys():
            curr_path = curr_topic.split('/')
            register_path = register_topic.split('/')
            match = True
            for index in range(len(register_path)):
                rp = register_path[index]
                if rp == '#':  # multi level match
                    break
                if rp == '+':  # single level match
                    continue
                cp = curr_path[index]
                if cp != rp:  # not match
                    match = False
                    break
            if match:
                match_list.append(register_topic)

        return match_list
