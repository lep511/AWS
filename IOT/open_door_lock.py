# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# This is importing the necessary libraries for the program to run.
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import time as t
import json
import base64
import time

# This is defining the variables that will be used in the program.
# Define ENDPOINT, CLIENT_ID, PATH_TO_CERTIFICATE, PATH_TO_PRIVATE_KEY, PATH_TO_AMAZON_ROOT_CA_1, MESSAGE, TOPIC, and RANGE
ENDPOINT = "akcmlgauu3otm-ats.iot.us-east-1.amazonaws.com"
CLIENT_ID = "basicPubSub"
PATH_TO_CERTIFICATE = "smart_lock_simulator.cert.pem"
PATH_TO_PRIVATE_KEY = "smart_lock_simulator.private.key"
PATH_TO_AMAZON_ROOT_CA_1 = "root-CA.crt"
TOPIC = "smart_door/actuator"
TIMEOUT = 1

def on_message_received(topic, payload, dup, qos, retain, **kwargs):
    """
    It prints the topic and payload of the message received
    
    :param topic: The topic the message was received on
    :param payload: The payload of the message
    :param dup: boolean, True if the message is a duplicate
    :param qos: Quality of Service, can be 0, 1, or 2
    :param retain: If set to True, the message will be retained by the broker
    """
    print("\nReceived message from topic " + topic)
    result_json = json.loads(payload)
    if(result_json['permission'] == 'granted'):
        print('Access GRANTED, opening door!!!')
    else:
        print('Access DENIED, the door remains closed!!!')

def main():
    """
    It connects to the AWS IoT MQTT broker, subscribes to a topic, and then waits for messages to arrive
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

    print("Subscribing to topic " + TOPIC)
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=TOPIC,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_message_received)

    subscribe_result = subscribe_future.result(TIMEOUT)
    print("Subscribed with {}".format(str(subscribe_result['qos'])))

    while True:
        time.sleep(0.3)

    print('Publish End')
    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()

if __name__ == "__main__":
    main()