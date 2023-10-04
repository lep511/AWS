# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# This is importing the necessary libraries for the program to run.
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import time as t
import json
import base64
import sys

# This is defining the variables that will be used in the program.
# Define ENDPOINT, CLIENT_ID, PATH_TO_CERTIFICATE, PATH_TO_PRIVATE_KEY, PATH_TO_AMAZON_ROOT_CA_1, MESSAGE, TOPIC, and RANGE.
ENDPOINT = "<Endpoint>"
CLIENT_ID = "basicPubSub"
PATH_TO_CERTIFICATE = "smart_lock_simulator.cert.pem"
PATH_TO_PRIVATE_KEY = "smart_lock_simulator.private.key"
PATH_TO_AMAZON_ROOT_CA_1 = "root-CA.crt"
TOPIC = "smart_door/photo"
IMAGE_FILE_NAME = str(sys.argv[1])

def main():
    """
    `main()` connects to the AWS IoT MQTT broker, publishes a message to a topic, and then disconnects
    from the broker
    """
    # Spin up resources
    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
                endpoint=ENDPOINT,
                cert_filepath=PATH_TO_CERTIFICATE,
                pri_key_filepath=PATH_TO_PRIVATE_KEY,
                client_bootstrap=client_bootstrap,
                ca_filepath=PATH_TO_AMAZON_ROOT_CA_1,
                client_id=CLIENT_ID,
                clean_session=False,
                keep_alive_secs=6
                )
    print("Connecting to {} with client ID '{}'...".format(
            ENDPOINT, CLIENT_ID))
    # Make the connect() call
    connect_future = mqtt_connection.connect()
    # Future.result() waits until a result is available
    connect_future.result()
    print("Connected!")
    # Publish message to server desired number of times.
    print('Begin Publish')

    with open(IMAGE_FILE_NAME, "rb") as image2string:
        converted_string = base64.b64encode(image2string.read()).decode('utf-8')
    payload = {
        "data": converted_string
    }

    message = payload
    mqtt_connection.publish(topic=TOPIC, payload=json.dumps(message), qos=mqtt.QoS.AT_LEAST_ONCE)
    print("Published: '" + IMAGE_FILE_NAME + "' to the topic: " + TOPIC)

    print('Publish End')
    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()

if __name__ == "__main__":
    main()