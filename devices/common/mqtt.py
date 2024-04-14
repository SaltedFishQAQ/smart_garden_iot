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
        self.client.connect(self.broker, self.port)
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
        print("Connected to %s with result code: %d" % (self.broker, rc))
    
    def handle_message(self, client, userdata, msg):
        topic = msg.topic
        if topic in self.topic_handlers:
            self.topic_handlers[topic](client, userdata, msg)
        else:
            print(f"topic {topic} no match callback")
