# Import necessary libraries
from locust import User, TaskSet, events, task, between
import paho.mqtt.client as mqtt
import time
import json
import os
import subprocess

# Run a Python script to update a JSON file (update_json.py)
subprocess.run(["python", "update_json.py"])

# Initialize a global variable to keep track of MQTT client count
COUNTClient = 0

# Define the MQTT broker address
broker_address = "broker.mqttdashboard.com"

# Define constants for request type and publish timeout
REQUEST_TYPE = 'MQTT'
PUBLISH_TIMEOUT = 10000

# Define a function to update timestamps in a JSON data structure
def update_timestamp(data):
    for key, value in data.items():
        if isinstance(value, dict):
            if 'timestamp' in value:
                value['timestamp'] = int(time.time())
            else:
                update_timestamp(value)

# Define a custom event handler for Locust's request success
def fire_locust_success(**kwargs):
    events.request.fire(**kwargs)

# Define a function to increment the global client count
def increment():
    global COUNTClient
    COUNTClient = COUNTClient + 1

# Define a function to calculate time delta between two timestamps
def time_delta(t1, t2):
    return int((t2 - t1) * 1000)

# Define a function to check and replace '{clientID}' in MQTT topics with the client ID
def check_topic_options(topic: str, client_id: str):
    if "{clientID}" in topic:
        return topic.replace('{clientID}', str(client_id.decode('utf-8')))
    else:
        return topic

# Add command line argument parsing for the 'topic' argument
@events.init_command_line_parser.add_listener
def _(parser):
    parser.add_argument("--topic", type=str, help="The topic that the clients send messages to.")

# Add a listener for the 'test_start' event to print the custom 'topic' argument
@events.test_start.add_listener
def _(environment, **kw):
    print(f"Custom argument supplied: {environment.parsed_options.topic}")

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

        # Read JSON data from a file and update timestamps
        with open("data.json") as json_file:
            json_data = json.load(json_file)
        update_timestamp(json_data)
        payload = json.dumps(json_data)

        # Check and replace '{clientID}' in the topic with the client's ID
        topic = check_topic_options(self.topic, self.client._client_id)
        print(f'This is the {payload}')

        # Publish the MQTT message and record relevant information
        MQTTMessageInfo = self.client.publish(topic, payload, qos=0, retain=False)
        pub_mid = MQTTMessageInfo.mid
        print("Mid = " + str(pub_mid))
        self.client.pubmessage[pub_mid] = Message(
            REQUEST_TYPE, 0, topic, payload, self.start_time, PUBLISH_TIMEOUT, str(self.client._client_id)
        )
        MQTTMessageInfo.wait_for_publish()
        self.client.disconnect()
        self.client.loop_stop()
        time.sleep(5)

    wait_time = between(0.5, 10)

# Define the MQTTLocust user class
class MQTTLocust(User):
    tasks = {PublishTask}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        increment()
        client_id = "MyDevice - "  + str(COUNTClient)
        self.client = mqtt.Client(client_id)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish
        self.client.pubmessage = {}

    def on_start(self):
        PublishTask.topic = self.environment.parsed_options.topic

    def on_connect(self, client, userdata, flags, rc, props=None):
        fire_locust_success(
            request_type=REQUEST_TYPE,
            name='connect',
            response_time=0,
            response_length=0
        )

    def on_disconnect(self, client, userdata, rc, props=None):
        print("Disconnected result code " + str(rc))

    def on_publish(self, client, userdata, mid):
        end_time = time.time()
        message = self.client.pubmessage.pop(mid, None)
        if message:
            total_time = time_delta(message.start_time, end_time)
            fire_locust_success(
                request_type=REQUEST_TYPE,
                name=message.name,
                response_time=total_time,
                response_length=len(message.payload)
            )
