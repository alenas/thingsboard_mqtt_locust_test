import paho.mqtt.client as mqtt
from locust import User, events, TaskSet, task
import time

from config import REQUEST_TYPE, topic, device_tokens, broker_address, PUBLISH_TIMEOUT, qos
from payload import PayloadGenerator
import json

# Define a TaskSet for publishing MQTT messages
class PublishTask(TaskSet):
    generator = PayloadGenerator()

    @task(1)
    def task_pub(self):
        self.client.reconnect()
        #self.client.loop_start()

        #generator = PayloadGenerator()
        payload = json.dumps(self.generator.next())
        print(f'This is the {payload}')

        start_time = time.time()
        # Publish the MQTT message and record relevant information
        MQTTMessageInfo = self.client.publish(topic, payload, qos=qos, retain=False)
        pub_mid = MQTTMessageInfo.mid
        print(str(self.client._client_id) + "Mid = " + str(pub_mid))
        self.client.pubmessage[pub_mid] = Message(
            REQUEST_TYPE, qos, topic, payload, start_time, PUBLISH_TIMEOUT, str(self.client._client_id)
        )
        MQTTMessageInfo.wait_for_publish()

        #self.client.disconnect()
        #self.client.loop_stop()
        #time.sleep(.1)



# Initialize a global variable to keep track of MQTT client count
COUNTClient = 0

# Define a function to increment the global client count
def increment():
    global COUNTClient
    COUNTClient = COUNTClient + 1
    if COUNTClient >= len(device_tokens):
        COUNTClient = 0

@staticmethod
def time_delta(t1, t2):
	return int((t2 - t1) * 1000)

# Define a class to represent MQTT messages
class Message(object):
    def __init__(self, type, qos, topic, payload, start_time, timeout, name):
        self.type = type,
        self.qos = qos,
        self.topic = topic
        self.payload = payload
        self.start_time = start_time
        self.timeout = timeout
        self.name = name

# Define the MQTTLocust user class
class MQTTLocust(User):
    generator = PayloadGenerator()
    #tasks = [PublishTask]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        client_id = device_tokens[COUNTClient]
        increment()
        print("User: " + client_id)

        self.client = mqtt.Client(client_id=client_id, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.client.username_pw_set(username=client_id)
        #self.client.on_connect = self.on_connect
        #self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish
        self.client.pubmessage = {}
        print("init finished")
        #client.connect(host=broker_address, port=1883, keepalive=60)
        #client.disconnect()

    def on_start(self):
        # client_id = device_tokens[COUNTClient]
        # increment()
        # print("Client: " + client_id)

        # client = mqtt.Client(client_id=client_id, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        # client.username_pw_set(username=client_id)
        # client.on_connect = self.on_connect
        # client.on_disconnect = self.on_disconnect
        # client.on_publish = self.on_publish
        # client.pubmessage = {}
        print("Connecting to broker")
        self.client.connect(host=broker_address, port=1883, keepalive=60)
        self.client.disconnect()

        print("loop started")
        #self.client.disconnect()

    @task
    def publish(self):
        if self.client.is_connected() == False:
            print("Reconnecting")
            self.client.reconnect()
            #self.client.connect(host=broker_address, port=1883, keepalive=60)
            self.client.loop_start()

        print("Publishing task")
        #generator = PayloadGenerator()
        payload = json.dumps(self.generator.next())
        #print(f'This is the {payload}')

        start_time = time.time()
        # Publish the MQTT message and record relevant information
        MQTTMessageInfo = self.client.publish(topic, payload, qos=qos, retain=False)
        pub_mid = MQTTMessageInfo.mid
        print(str(self.client._client_id) + "Mid = " + str(pub_mid))
        self.client.pubmessage[pub_mid] = Message(
            REQUEST_TYPE, qos, topic, payload, start_time, PUBLISH_TIMEOUT, str(self.client._client_id)
        )
        MQTTMessageInfo.wait_for_publish()


    def on_stop(self):
        self.client.disconnect()
        self.client.loop_stop()
        print("loop stopped")

	# client, userdata, flags, reason_code, properties
    def on_connect(self, client, userdata, flags, rc, props=None):
        print("Connected with result code: " + str(rc))
        # events.request.fire(
        #     request_type=REQUEST_TYPE,
        #     name='connect',
        #     response_time=0,
        #     response_length=0
        # )

    # disconnect_callback(client, userdata, disconnect_flags, reason_code, properties)
    def on_disconnect(self, client, userdata, flags, rc, props=None):
        print("Disconnected result code: " + str(rc))

    # publish_callback(client, userdata, mid, reason_code, properties)
    def on_publish(self, client, userdata, mid, rc, props=None):
        end_time = time.time()
        message = self.client.pubmessage.pop(mid, None)
        if message:
            total_time = time_delta(message.start_time, end_time)
            events.request.fire(
                request_type=REQUEST_TYPE,
                name=message.name,
                response_time=total_time,
                response_length=len(message.payload)
            )

