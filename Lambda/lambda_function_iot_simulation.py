import json
import boto3
import uuid
import time
import datetime
import os
runtime_region = os.environ['AWS_REGION']
client = boto3.client('iot-data', region_name=runtime_region)
curr_datetime = datetime.datetime.utcnow()
curr_datetime_iso = curr_datetime.isoformat()
transitVehicles = {
'401869876': {'vin':'8763b61e-2945-47ac-b3fb-bf16d4d316a6', 'coordinates': [
    [-96.81865811347961, 33.07027192165384],
    [-96.81866884231567, 33.06886035700154]
  ]},
'401848734' : {'vin':'b4e2078b-2a1c-42ff-b8cc-5a66542698ca', 'coordinates': [
    [-96.71615481376648, 32.976160072356514],
    [-96.71669125556946, 32.97521502639376],
    [-96.71714186668396, 32.97449498458644],
    [-96.71669125556946, 32.97521502639376],
    [-96.71714186668396, 32.97449498458644]
  ]}
 }
enterVehicles = {
'401869876': {'vin': '8763b61e-2945-47ac-b3fb-bf16d4d316a6', 'coordinates': [
    [-96.81865811347961, 33.067223992568664],
    [-96.81903362274169, 33.066684525097415],
    [-96.81945204734802, 33.06725096585542],
    [-96.82041764259338, 33.06730491240415],
    [-96.82165145874023, 33.06731390349237]
  ]},
'401848734': {'vin': 'b4e2078b-2a1c-42ff-b8cc-5a66542698ca', 'coordinates': [
    [-96.7190408706665, 32.973657928606265],
    [-96.71915888786316, 32.9731718924609],
    [-96.7198133468628, 32.972703855126255]
  ]}
}
exitVehicles = {
'401869876': {'vin': '8763b61e-2945-47ac-b3fb-bf16d4d316a6', 'coordinates': [
    [-96.8230676651001, 33.06703517932991],
    [-96.82345390319824, 33.06815007068296],
    [-96.82410836219788, 33.06848273714088],
    [-96.82414054870605, 33.06950770156399],
    [-96.82411909103394, 33.07040678333363],
    [-96.8241512775421, 33.071215949071764],
    [-96.82410836219788, 33.07238473088975],
    [-96.82406544685364, 33.0731579164827]
  ]},
'401848734': {'vin': 'b4e2078b-2a1c-42ff-b8cc-5a66542698ca', 'coordinates': [
    [-96.72067165374756, 32.97230782159811],
    [-96.72159433364868, 32.971434741411095],
    [-96.72158360481262, 32.97068766594556],
    [-96.72160506248474, 32.969823570779184],
    [-96.72088623046875, 32.96862642496605]
  ]}
}

def parseMessages(vehicles):
    for key in vehicles:
        coords = vehicles[key]['coordinates']
        vin = vehicles[key]['vin']
        for values in coords:
            device_position_msg = {}
            device_position_msg['eventid'] = str(uuid.uuid4())
            device_position_msg['vehicleid'] = key
            device_position_msg['vin'] = vin
            device_position_msg['timestamp'] = curr_datetime_iso
            device_position_msg['position'] = values
            messageJson = json.dumps(device_position_msg)
            response = client.publish(
                topic='iot/fleet/location',
                qos=1,
                payload=messageJson
            )
            time.sleep(3)
            print(response)


def lambda_handler(event, context):
    parseMessages(transitVehicles)
    parseMessages(enterVehicles)
    parseMessages(exitVehicles)


    return {
        'statusCode': 200,
        'body': json.dumps('Published to topic')
    }
