import base64
import boto3
import json
import os
import requests
from requests_aws4auth import AWS4Auth
from datetime import datetime

service = 'es'
credentials = boto3.Session().get_credentials()
dynamodb_client = boto3.client('dynamodb')
session = boto3.session.Session()
region = session.region_name
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

host = os.environ['OPENSEARCH_ENDPOINT']
index = 'ambulance-index'
datatype = '_doc'
url = host + '/' + index + '/' + datatype + '/'

headers = { "Content-Type": "application/json" }

client = boto3.client(
    'location'
)

def lambda_handler(event, context):
    
    count = 0
    for record in event['Records']:
        try:
            id = record['eventID']
            timestamp = record['kinesis']['approximateArrivalTimestamp']
            
            # Kinesis data is base64-encoded, so decode here
            data = base64.b64decode(record['kinesis']['data'])
            json_data = json.loads(data)

            route = client.calculate_route(
                CalculatorName='connected-ambulances',
                DepartNow=False,
                IncludeLegGeometry=True,
                DeparturePosition=[
                    json_data['data']['longitude'], json_data['data']['latitude']
                ],
                DestinationPosition=[
                    json_data['data']['destination_longitude'], json_data['data']['destination_latitude']
                ]
            )
            eta = round(route['Summary']['DurationSeconds']/60)
            print(eta)
            
            line_string = route['Legs'][0]['Geometry']['LineString']
            
            print(line_string)
            
            
    
            # Create the JSON document
            document = { 
                "id": id, 
                "date_time": json_data['data']['date_time'],
                
                "ambulance_location": { 
                    "lat": json_data['data']['latitude'],
                    "lon": json_data['data']['longitude']
                 },
                 
                "hospital_location": { 
                    "lat": json_data['data']['destination_latitude'],
                    "lon": json_data['data']['destination_longitude']
                 },
                 
                "route": {
                    "type" : "LineString",
                    "coordinates" : line_string
                 },
                
                "eta": eta,
                "ambulance_id": json_data['data']['ambulance_id'],
                "heart_rate": json_data['data']['heart_rate'],
                "systolic_blood_pressure": json_data['data']['systolic_blood_pressure'],
                "diastolic_blood_pressure": json_data['data']['diastolic_blood_pressure'],
                "blood_oxygen_level": json_data['data']['blood_oxygen_level'],
                "body_temperature": json_data['data']['body_temperature'],

            }

            # Index the document
            print('---------------------------------------------------------------')
            print('Sending doc to opensearch...')

            r = requests.put(url + id, auth=awsauth, json=document, headers=headers)
            print(r)
            print(r.content)

            count += 1
        except Exception as e: 
            print(e)
            
    return 'Processed ' + str(count) + ' items.'