import boto3
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
import calendar

# Define ENDPOINT, CLIENT_ID, PATH_TO_CERTIFICATE, PATH_TO_PRIVATE_KEY, PATH_TO_AMAZON_ROOT_CA_1, MESSAGE, TOPIC, and RANGE
ENDPOINT = "<REPLACE_WITH_IoT_ENDPOINT>"
CLIENT_ID = "dcs_simulator"
PATH_TO_CERTIFICATE = "/home/ec2-user/environment/DCS.cert.pem"
PATH_TO_PRIVATE_KEY = "/home/ec2-user/environment/DCS.private.key"
PATH_TO_AMAZON_ROOT_CA_1 = "/home/ec2-user/environment/root-CA.crt"
TOPIC = "dcs/telemetry"

def main():
    init_route()
    
def init_route():
    client = boto3.client(
        'location',
        region_name='us-east-1'
    )
    
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

    count = 0
    while(count < 10):
        now = datetime.now()
        date_time = now.strftime("%Y-%m-%d %H:%M:%S")
    
        ts = calendar.timegm(time.gmtime())

        payload = {
            'time': ts,
            'temperature': random.randint(849, 855)
        }
    
        message = payload
        result = mqtt_connection.publish(topic=TOPIC, payload=json.dumps(message), qos=mqtt.QoS.AT_LEAST_ONCE)
        print("Published: '" + str(payload) + "' to the topic: " + TOPIC)
        t.sleep(1)
        count += 1
                    
if __name__ == "__main__":
    main()