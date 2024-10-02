# ThingsBoard MQTT Locust Load Testing Script Documentation

## Introduction

The "mqtt.py" script is a Python program designed to perform load testing on ThingsBoard MQTT (Message Queuing Telemetry Transport) brokers using the Locust load testing framework. This script simulates multiple MQTT clients publishing messages to a broker and measures the performance of the broker under load.

## Table of Contents

1. [Installation](#installation)
2. [Usage](#usage)
3. [MQTT configuration](#configuration)
4. [Locust configuration](#locust)
5. [Script Structure](#script-structure)
6. [Customization](#customization)
7. [Results and Reporting](#results-and-reporting)
8. [Example Scenario](#example-scenario)
9. [Troubleshooting](#troubleshooting)
10. [Contributing](#contributing)
11. [License](#license)

## Installation <a name="installation"></a>

- Clone or download the script from the GitHub repository.
- Ensure you have Python 3.x installed on your system.
- Install the required Python libraries using pip:

```bash
pip install -r requirement.txt
```

or

```bash
pip install locust paho-mqtt
```


## Usage <a name="usage"></a>

To use the script, follow these steps:

Open a terminal or command prompt.

Navigate to the directory containing the "mqtt.py" script.

Run locust with configuration stored in "pyproject.toml":

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

## MQTT Configuration <a name="configuration"></a>

MQTT connection configuration is stored in "config.py"
```
# Device tokens - there should be at least one
device_tokens = ["tb_access_token"]

# Define the MQTT broker address and port
tb_address = "your.server.com"
tb_port = 1883

# Define the MQTT topic and QoS to subscribe to
mqtt_topic = "v1/lptrk/gps"
mqtt_qos = 1

# Define constants for request type and publish timeout
REQUEST_TYPE = 'MQTT'
PUBLISH_TIMEOUT = 10000
```

## Locust configuration <a name="locust"></a>

Locust configuration is stored in "pyproject.toml"

```
[tool.locust]
locustfile = "mqtt.py"
headless = true
expect-workers = 1
spawn-rate = 1
run-time = "1m"
only-summary = 1
```

## Script Structure <a name="script-structure"></a>
The script is structured into several sections:

Importing required libraries.
Initializing global variables.
Defining functions for MQTT message handling and topic customization.
Handling command-line arguments.
Defining the structure of MQTT messages.
Creating a TaskSet for publishing MQTT messages.
Creating the MQTTLocust class for load testing.
Configuring Locust tasks.
Handling MQTT connection, disconnection, and message publishing.
Running the load test using Locust.

## Customization <a name="customization"></a>

You can customize the script by modifying the following parameters:

MQTT broker address (broker_address).
MQTT request type (REQUEST_TYPE).
Publish timeout (PUBLISH_TIMEOUT).
JSON data file ("data.json").
Message publishing frequency (wait_time in the TaskSet).
Running the Tests <a name="running-the-tests"></a>
Run the script using the locust command as described in the "Usage" section.

Configure the number of clients, hatch rate, and other test parameters via the Locust web interface.

Start the test from the web interface, and the script will simulate MQTT clients publishing messages to the broker.

## Results and Reporting <a name="results-and-reporting"></a>

Locust provides real-time performance metrics and reporting through its web interface or terminal output.

You can view various statistics such as response times, request rates, and failures.

Generate and save detailed reports for analysis.

## Example Scenario <a name="example-scenario"></a>
Here's an example scenario:

You want to test the performance of an MQTT broker under load.

You have an MQTT topic, e.g., "my/topic", to which clients publish JSON data.

You run the script with the appropriate configuration and command-line arguments.

Using the Locust web interface, you simulate 100 clients with a hatch rate of 10 clients per second.

The script sends MQTT messages to the broker, measuring response times and other metrics.

You analyze the results to assess the broker's performance.

## Troubleshooting <a name="troubleshooting"></a>
* Did you set correct values in "config.py"? 

## Contributing <a name="contributing"></a>
Contributions to this script are welcome. Please fork the repository, make your changes, and submit a pull request.

## License <a name="license"></a>
This script is released under the MIT License.
