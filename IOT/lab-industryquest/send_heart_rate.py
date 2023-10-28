# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import time as t
import json
import base64
import sys
import csv
from datetime import datetime
import time
import random
import os

# Define ENDPOINT, CLIENT_ID, PATH_TO_CERTIFICATE, PATH_TO_PRIVATE_KEY, PATH_TO_AMAZON_ROOT_CA_1, MESSAGE, TOPIC, and RANGE
ENDPOINT = os.getenv('ENDPOINT')
PATH_TO_CERTIFICATE = os.getenv('PATH_TO_CERTIFICATE')
PATH_TO_PRIVATE_KEY = os.getenv('PATH_TO_PRIVATE_KEY')
PATH_TO_AMAZON_ROOT_CA_1 = "root-CA.crt"
CLIENT_ID = "wearable-heart-monitor"
TOPIC = "wearable-heart-monitor/heart_rate"
DATASET = "heart_rate.csv"
WEARABLE_ID = 1


def main():
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

    # Iterate over each row in the csv file
    # using reader object
    while True:
        # Open file
        with open(DATASET) as file_obj:
            # Skips the heading
            # Using next() method
            heading = next(file_obj)

            # Create reader object by passing the file
            # object to reader method
            reader_obj = csv.reader(file_obj)

            for row in reader_obj:
                now = datetime.now()
                date_time = now.strftime("%Y-%m-%d %H:%M:%S")
                payload = {
                    "date_time": date_time,
                    "wearable_id": WEARABLE_ID,
                    "heart_rate": int(row[1])
                }
                message = payload
                mqtt_connection.publish(topic=TOPIC, payload=json.dumps(
                    message), qos=mqtt.QoS.AT_LEAST_ONCE)
                print("Published: '" + str(payload) +
                      "' to the topic: " + TOPIC)
                t.sleep(1)

    print('Publish End')
    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()


if __name__ == "__main__":
    main()
