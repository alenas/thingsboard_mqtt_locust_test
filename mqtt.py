import paho.mqtt.client as mqtt
from locust import User, events, TaskSet, task
import time

from config import REQUEST_TYPE, topic, device_tokens, broker_address, PUBLISH_TIMEOUT, qos
from payload import PayloadGenerator
import json

# Define a TaskSet for publishing MQTT messages
class PublishTask(TaskSet):
    def on_start(self):
        self.client.connect(host=broker_address, port=1883, keepalive=60)
        self.client.disconnect()

    @task(1)
    def task_pub(self):
        self.client.reconnect()
        self.client.loop_start()
        self.start_time = time.time()

        generator = PayloadGenerator()
        payload = json.dumps(generator.next())

        #print(f'This is the {payload}')

        # Publish the MQTT message and record relevant information
        MQTTMessageInfo = self.client.publish(topic, payload, qos=qos, retain=False)
        pub_mid = MQTTMessageInfo.mid
        print(str(self.client._client_id) + "Mid = " + str(pub_mid))
        self.client.pubmessage[pub_mid] = Message(
            REQUEST_TYPE, qos, topic, payload, self.start_time, PUBLISH_TIMEOUT, str(self.client._client_id)
        )
        MQTTMessageInfo.wait_for_publish()
        self.client.disconnect()
        self.client.loop_stop()
        #time.sleep(.1)

    #wait_time = between(0.5, 10)


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
    tasks = {PublishTask}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        client_id = device_tokens[COUNTClient]
        increment()
        self.client = mqtt.Client(client_id=client_id, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.client.username_pw_set(username=client_id)
        #self.client.on_connect = self.on_connect
        #self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish
        self.client.pubmessage = {}

    def on_start(self):
        PublishTask.topic = topic

	# client, userdata, flags, reason_code, properties
    def on_connect(self, client, userdata, flags, rc, props=None):
        events.request.fire(
            request_type=REQUEST_TYPE,
            name='connect',
            response_time=0,
            response_length=0
        )

    # disconnect_callback(client, userdata, disconnect_flags, reason_code, properties)
    #def on_disconnect(self, client, userdata, flags, rc, props=None):
    #    print("Disconnected result code " + str(rc))

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

