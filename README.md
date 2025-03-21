# ThingsBoard MQTT Locust Load Testing Script Documentation

## Introduction

The "mqtt.py" script is a Python program designed to perform load testing on ThingsBoard MQTT (Message Queuing Telemetry Transport) brokers using the Locust load testing framework. This script simulates multiple MQTT clients publishing messages to a broker and measures the performance of the broker under load.

The "device_generator.py" script is a Phyton script, which creates a number of test devices on Thingsboard (for example 100) so you could use them for load testing.  

## Table of Contents

1. [Installation](#installation)
2. [Usage](#usage)
3. [MQTT configuration](#mqtt-configuration)
4. [Locust configuration](#locust-configuration)
5. [ThingsBoard provisioning](#thingsboard-device-provisioning)
7. [Results and Reporting](#results-and-reporting)
8. [Example Scenario](#example-scenario)
9. [Troubleshooting](#troubleshooting)
10. [Contributing](#contributing)
11. [License](#license)

## Installation {#installation}

- Clone or download the script from the GitHub repository.
- Ensure you have **Python 3.x** and **pip** installed on your system.
- Install the required Python libraries using pip:

```bash
pip install -r requirement.txt
```

or

```bash
pip install locust paho-mqtt
```


## Usage {#usage}

Follow these steps:

1. Open a terminal or command prompt.

2. Navigate to the directory containing scripts.

3. Check [MQTT configuration](#mqtt-configuration) and [locust configuration](#locust-configuration)

4. Check "payload.py" to see what data will be sent to the device.

5. Create "credentials.py":

Run **"python device_generator.py"** if you need to create test devices. Script will
prompt for all the required data. Make sure that Thingsboard device profile allows automatic [device provisioning](#thingsboard-device-provisioning).

If you create 2 devices, their ThingsBoard access tokens will be saved to 
"credentials.py", like this:

```
# This file is autogenerated by device_generator.py
device_tokens = ['5bgOMX328hgLD','Udyz5XvdvmOTvOrD']
```

otherwise create "credentials.py" file manually like above.

6. Run locust with configuration stored in "pyproject.toml":

```bash
locust
```

or

Run the script with the desired command-line arguments. For example:

```bash
locust -f mqtt.py --headless --users 10 --spawn-rate 1
```

or 

Open a web browser and navigate to the Locust web interface (by default, it's http://localhost:8089).

Configure the number of users (clients) and the hatch rate for your load test.

Start the load test from the web interface.

## MQTT Configuration {#mqtt-configuration}

MQTT connection configuration is stored in "config.py".

If you set port 8883, it will try to set TLS without client certificates. So this is not properly tested yet and it might not work.

UDP connections (mqtt_qos=0) do not work yet.

```
# Define the MQTT broker address and port
tb_address = "your.server.com"
tb_port = 1883

# Define the MQTT topic and QoS to subscribe to
mqtt_topic = "v1/devices/me/telemetry"
mqtt_qos = 1

# Define constants for request type and publish timeout
REQUEST_TYPE = 'MQTT'
PUBLISH_TIMEOUT = 10000
```

## Locust configuration {#locust-configuration}

Locust configuration is stored in "pyproject.toml"

```
[tool.locust]
locustfile = "mqtt.py"
headless = true
expect-workers = 1
spawn-rate = 1
run-time = "1m"
only-summary = 1
users = 100 # should equal number of devices you are testing
```

## ThingsBoard device provisioning {#profile}

To be able to generate test devices with "device_generator.py" you need to make sure ThingsBoard device profile is set up correctly:
- Open ThingsBoard **Device profiles**. 
- Open **Device provisioning** tab.
- Set "Provisioning strategy" to "Allow to create new devices"
- Enter or copy "Provision device key" and "Provision device secret" - you will need to enter these two values into "device_generator.py" when requested.

## Results and Reporting {#results-and-reporting}

Locust provides real-time performance metrics and reporting through its web interface or terminal output.

You can view various statistics such as response times, request rates, and failures.

Generate and save detailed reports for analysis.

## Example Scenario {#example-scenario}

Here's an example scenario:

You want to test the performance of an MQTT broker under load.

You have an MQTT topic, e.g., "my/topic", to which clients publish JSON data.

You run the script with the appropriate configuration and command-line arguments.

Using the Locust web interface, you simulate 100 clients with a hatch rate of 10 clients per second.

The script sends MQTT messages to the broker, measuring response times and other metrics.

You analyze the results to assess the broker's performance.

## Troubleshooting {#troubleshooting}

* Did you set correct values in "config.py"? 

## Contributing {#contributing}

Contributions to this script are welcome. Please fork the repository, make your changes, and submit a pull request.

## License {#license}

This script is released under the MIT License.
