import paho.mqtt.client as mqtt
from locust import User, events, TaskSet, task, run_single_user
import time

from config import REQUEST_TYPE, mqtt_topic, mqtt_qos, tb_address, tb_port, PUBLISH_TIMEOUT
from payload import PayloadGenerator
from credentials import device_tokens
import json

# Initialize a global variable to keep track of MQTT client count
COUNTClient = 0

@staticmethod
def get_client_id():
    global COUNTClient
    cc = COUNTClient
    COUNTClient = COUNTClient + 1
    if COUNTClient >= len(device_tokens):
        COUNTClient = 0
    return device_tokens[cc]

@staticmethod
def time_delta(t1, t2):
	return int((t2 - t1) * 1000)

# Define short message
class Message(object):
    def __init__(self, id, start_time, length):
        self.id = id
        self.start_time = start_time
        self.length = length

# Define the MQTTLocust user class
class MQTTLocust(User):
    generator = PayloadGenerator()
    unacked_publish = {}
    client_id = None
    # spawn only 1 user per device
    fixed_count = len(device_tokens)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = get_client_id()
        print("User: " + self.client_id)

        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.client.username_pw_set(username=self.client_id)
        self.client.on_connect = self.on_connect
        self.client.on_connect_fail = self.on_connect_fail
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish
        self.client.user_data_set(self.unacked_publish)

    def on_start(self):
        # set SSL if required
        if tb_port == 8883:
            self.client.tls_set()
        self.client.connect(host=tb_address, port=tb_port, keepalive=60)
        self.client.loop_start()

    @task
    def publish(self):
        if self.client.is_connected() == False:
            #print(str(self.client_id) + " >> Reconnecting")
            self.client.reconnect()
            self.client.loop_start()

        payload = json.dumps(self.generator.next())

        start_time = time.time()
        # Publish the MQTT message and record relevant information
        MQTTMessageInfo = self.client.publish(mqtt_topic, payload, qos=mqtt_qos, retain=False)
        pub_mid = MQTTMessageInfo.mid
        self.unacked_publish[pub_mid] = Message(self.client_id, start_time, len(payload))
        #print(str(self.client_id) + " > Mid = " + str(pub_mid))

        while len(self.unacked_publish):
            time.sleep(0.01)

        if mqtt_qos > 0:
            MQTTMessageInfo.wait_for_publish()


    def on_stop(self):
        self.client.disconnect()
        self.client.loop_stop()

	# client, userdata, flags, reason_code, properties
    def on_connect(self, client, userdata, flags, rc, props=None):
        print(str(self.client_id) + " >> Connected with result code: " + str(rc))

    def on_connect_fail(self, client, userdata, rc, props=None):
        print(str(self.client_id) + " >>> Failed to connect: " + str(rc))
        events.request.fire(
            request_type=REQUEST_TYPE,
            name='connect_fail',
            response_time=0,
            response_length=0,
            exception = 'connect_fail'
        )

    # disconnect_callback(client, userdata, disconnect_flags, reason_code, properties)
    def on_disconnect(self, client, userdata, flags, rc, props=None):
        print(str(self.client_id) + " >> Disconnected result code: " + str(rc))

    # publish_callback(client, userdata, mid, reason_code, properties)
    def on_publish(self, client, userdata, mid, rc, props=None):
        end_time = time.time()
        try:
            message = userdata.pop(mid, None)
        except KeyError:
            print(str(self.client_id) + " >>> on_publish() is called with a mid not present in unacked_publish")

        #message = self.client.pubmessage.pop(mid, None)
        if message:
            total_time = time_delta(message.start_time, end_time)
            events.request.fire(
                request_type=REQUEST_TYPE,
                name=message.id,
                response_time=total_time,
                response_length=message.length
            )

# if launched directly, e.g. "python3 debugging.py", not "locust -f debugging.py"
if __name__ == "__main__":
    run_single_user(MQTTLocust)