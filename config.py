# Device tokens - there should be at least one
device_tokens = ["04nhpekxphe5wv9lffn6","uo7lel4valfrieibbwph","t902hxlcuhgwoo3nedoq"]
#["dy6it7odoopo2cutmu1x"]

# Define the MQTT broker address
broker_address = "age.dev.telemetrak.net" # "3.teststack.telemetrak.net"
#"age.dev.telemetrak.net"

# Define the MQTT topic to subscribe to
topic = "v1/devices/me/telemetry"
qos = 1

# Define constants for request type and publish timeout
REQUEST_TYPE = 'MQTT'
PUBLISH_TIMEOUT = 10000
