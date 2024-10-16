import paho.mqtt.client as mqtt
from paho.mqtt.client import Client
from json import dumps, loads
import time

from config import REQUEST_TYPE, mqtt_topic, mqtt_qos, tb_address, tb_port, PUBLISH_TIMEOUT


# Define short message
class Config(object):
    def __init__(self, host, port, provision_key, provision_secret, number_of_devices, device_name):
        self.host = host
        self.port = port
        self.provision_key = provision_key
        self.provision_secret = provision_secret
        self.number_of_devices = number_of_devices
        self.device_name = device_name

# Collects data
def collect_required_data():
    print("\n\n", "="*80, sep="")
    print(" "*10, "\033[1m\033[94mThingsBoard device provisioning with access token authorization. MQTT API\033[0m", sep="")
    print("="*80, "\n\n", sep="")
    host = input("Please write your ThingsBoard \033[93mhost\033[0m or leave it blank to use default (%s): " % tb_address)
    if host == "":
        host = tb_address
    port = input("Please write your ThingsBoard \033[93mport\033[0m or leave it blank to use default (%s): " % tb_port)
    if port == "":
        port = tb_port
    provision_key = input("Please write \033[93mprovisioning key\033[0m: ")
    provision_secret = input("Please write \033[93mprovisioning secret\033[0m: ")
    num = input("Please write \033[93mnumber of devices to generate\033[0m: ")
    device_name = input("Please write \033[93mdevice name\033[0m prefix: ")
    if device_name == "":
        device_name = "device"
    print("\n", "="*80, "\n", sep="")
    return Config(host, int(port), provision_key, provision_secret, int(num), device_name)


class ProvisionClient(Client):
    PROVISION_REQUEST_TOPIC = "/provision/request"
    PROVISION_RESPONSE_TOPIC = "/provision/response"
    NUMBER_OF_DEVICES = 0
    CREDENTIALS = set()
    DEVICE_NAME = ""
    IS_CONNECTED = False

    def __init__(self, config: Config):
        super().__init__(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self._host = config.host
        self._port = config.port
        self.NUMBER_OF_DEVICES = config.number_of_devices
        self._username = "provision" # do not change this, as it will not connect
        self.DEVICE_NAME = config.device_name
        self.on_connect = self.__on_connect
        self.on_disconnect = self.__on_disconnect
        self.on_message = self.__on_message
        self.__provision_request = {"provisionDeviceKey": config.provision_key,  # Provision device key, replace this value with your value from device profile.
                         "provisionDeviceSecret": config.provision_secret,  # Provision device secret, replace this value with your value from device profile.
                         }
        
    def __on_disconnect(self, client: Client, userdata, flags, rc, props=None):  # Callback for disconnect
        self.IS_CONNECTED = False
        print("Disconnected from ThingsBoard: %s " % str(rc))

    def __on_connect(self, client: Client, userdata, flags, rc, props=None):  # Callback for connect
        if rc == 0:
            print("Connected to ThingsBoard")
            self.IS_CONNECTED = True
            self.subscribe(self.PROVISION_RESPONSE_TOPIC, qos=1)  # Subscribe to provisioning response topic
        else:
            print("Cannot connect to ThingsBoard: %s" % str(rc))

    def __on_message(self, client, userdata, msg):
        decoded_payload = msg.payload.decode("UTF-8")
        print("Received data from ThingsBoard: %s" % decoded_payload)
        decoded_message = loads(decoded_payload)
        provision_device_status = decoded_message.get("status")
        if provision_device_status == "SUCCESS":
            token = decoded_message["credentialsValue"]
            self.CREDENTIALS.add(token)
        else:
            print("Provisioning was unsuccessful with status %s and message: %s" % (provision_device_status, decoded_message["errorMsg"]))

    def provision(self):
        print("Connecting to ThingsBoard")
        try:
            self.connect(self._host, self._port, 60)
            self.loop_start()
        except:
            print("Failed connecting")
            exit(1)

        for i in range(0, 3):
            if self.IS_CONNECTED:
                break
            else:
                time.sleep(1)

        if not self.IS_CONNECTED:
            print("Not connected. Exiting...")
            self.loop_stop()
            exit(1)

        self.create_devices()

        while len(self.CREDENTIALS) < self.NUMBER_OF_DEVICES:
            if not self.IS_CONNECTED:
                break
            time.sleep(1)

        self.disconnect()
        self.loop_stop()
        self.__save_credentials(self.CREDENTIALS)

    def create_devices(self):
        for i in range(1, self.NUMBER_OF_DEVICES + 1):
            self.__create_device(i)

    def __create_device(self, device_id):
        self.__provision_request["deviceName"] = "%s_%d" % (self.DEVICE_NAME, device_id)
        provision_request = dumps(self.__provision_request)
        print("Sending provisioning request %s" % device_id)
        MQTTMessageInfo = self.publish(self.PROVISION_REQUEST_TOPIC, provision_request, qos=1)  # Publishing provisioning request topic
        MQTTMessageInfo.wait_for_publish(1)

    @staticmethod
    def __save_credentials(credentials):
        with open("credentials.py", "w") as credentials_file:
            credentials_file.write("# This file is autogenerated by device_generator.py\n")
            credentials_file.write("device_tokens = ['")
            credentials_file.write("','".join(credentials))
            credentials_file.write("']\n")


if __name__ == '__main__':

    config = collect_required_data()

    provision_client = ProvisionClient(config)
    provision_client.provision()
