# Device tokens - there should be at least one
device_tokens = ["",""]

# Define the MQTT broker address
tb_address = "age.dev.telemetrak.net"
tb_port = 1883

# Define the MQTT topic to subscribe to
mqtt_topic = "v1/lptrk/gps"
mqtt_qos = 1

# Define constants for request type and publish timeout
REQUEST_TYPE = 'MQTT'
PUBLISH_TIMEOUT = 10000
