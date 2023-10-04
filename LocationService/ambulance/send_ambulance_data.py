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
import os

# Define ENDPOINT, CLIENT_ID, PATH_TO_CERTIFICATE, PATH_TO_PRIVATE_KEY, PATH_TO_AMAZON_ROOT_CA_1, MESSAGE, TOPIC, and RANGE
ENDPOINT = os.getenv('ENDPOINT')
CLIENT_ID = "ambulance-1"  # This should be the name of the Thing device created in the console
PATH_TO_CERTIFICATE = os.getenv('PATH_TO_CERTIFICATE')
PATH_TO_PRIVATE_KEY = os.getenv('PATH_TO_PRIVATE_KEY')
PATH_TO_AMAZON_ROOT_CA_1 = "/home/ec2-user/environment/root-CA.crt"
TOPIC = "ambulance/location_and_vital_signs" #The ambulances send messages to this MQTT topic 
DATASET = "/home/ec2-user/environment/vital_signs.csv"
AMBULANCE_ID = 1 #The ID of the ambulance
CALCULATOR_NAME='connected-ambulances' # The calculator created in the console.

DEPARTURE_LONGITUTE=-73.98504245471598
DEPARTURE_LATITUDE=40.75371912234989

DESTINATION_LONGITUTE=-73.89068380225616
DESTINATION_LATITUDE=40.8570520017933

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

    vital_sign_iterator = init_vital_sign()
    
    while True:
        
        route = client.calculate_route(
            CalculatorName=CALCULATOR_NAME,
            DepartNow=False,
            IncludeLegGeometry=True,
            DeparturePosition=[
                DEPARTURE_LONGITUTE,DEPARTURE_LATITUDE
            ],
            DestinationPosition=[
                DESTINATION_LONGITUTE,DESTINATION_LATITUDE
            ]
        )
        
        total_duration = int(route['Summary']['DurationSeconds'])
    
        points_list = []
        current_second = 0
        acumulated_seconds = 0
        
        for leg in route['Legs']:
            points_quantity = len(leg['Geometry']['LineString'])
            seconds_per_point = total_duration/(points_quantity-1)
            for point in leg['Geometry']['LineString']:
                latitude = point[1]
                longitude = point[0]
                second_to_play = round(acumulated_seconds)
                next_second_to_play = round(round(acumulated_seconds) + round(seconds_per_point))
                
                for i in range(second_to_play, next_second_to_play):
    
                    try:
                        sign = next(vital_sign_iterator)
                    except:
                        print('resetting iterator')
                        vital_sign_iterator = init_vital_sign()
                        
                    now = datetime.now()
                    #date_time = now.strftime("%m-%d-%Y %H:%M:%S")
                    date_time = now.strftime("%Y-%m-%dT%H:%M:%S.%sZ")
                    curr_time = round(time.time()*1000)
    
                    payload = {
                        "data": {
                            "date_time": curr_time,
                            'latitude': latitude,
                            'longitude': longitude,
                            'destination_latitude': DESTINATION_LATITUDE,
                            'destination_longitude': DESTINATION_LONGITUTE,
                            'second_to_play': i,
                            "ambulance_id": sign['ambulance_id'],
                            "heart_rate": sign['heart_rate'],
                            "systolic_blood_pressure": sign['systolic_blood_pressure'],
                            "diastolic_blood_pressure": sign['diastolic_blood_pressure'],
                            "blood_oxygen_level": sign['blood_oxygen_level'],
                            "body_temperature": sign['body_temperature'],
                        }
                    }

                    if i > total_duration:
                        break
                    
                    message = payload
                    #result = mqtt_connection.publish(topic=TOPIC, payload=json.dumps(message), qos=mqtt.QoS.AT_LEAST_ONCE)
                    result = mqtt_connection.publish(topic=TOPIC, payload=json.dumps(message), qos=mqtt.QoS.AT_LEAST_ONCE)
                    
                    
                    print("Published: '" + str(payload) + "' to the topic: " + TOPIC)
                    t.sleep(1)
                    
                current_second = current_second + 1
                acumulated_seconds = acumulated_seconds+seconds_per_point
    
def init_vital_sign():
    vital_sign_list = []
    with open(DATASET) as file_obj:
        # Skips the heading
        # Using next() method
        heading = next(file_obj)
          
        # Create reader object by passing the file 
        # object to reader method
        reader_obj = csv.reader(file_obj)
    
        for row in reader_obj:
            now = datetime.now()
            #date_time = now.strftime("%m-%d-%Y %H:%M:%S")
            date_time = now.strftime("%Y-%m-%dT%H:%M:%S.%sZ")
            curr_time = round(time.time()*1000)

            record = {
                "ambulance_id": AMBULANCE_ID,
                "heart_rate": int(row[1]),
                "systolic_blood_pressure": int(row[2])+random.randint(-5,5),
                "diastolic_blood_pressure": int(row[3])+random.randint(-5,5),
                "blood_oxygen_level": int(row[4])+random.randint(-1,1),
                "body_temperature": float(row[5])+round(random.uniform(-0.1, 0.1),1)
            }
            
            vital_sign_list.append(record)
        

        vital_sign_iterator = iter(vital_sign_list)
        return vital_sign_iterator
            
            
if __name__ == "__main__":
    main()
