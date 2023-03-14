from __future__ import print_function
from aws_kinesis_agg.deaggregator import deaggregate_records, iter_deaggregate_records
from decimal import Decimal
import base64
import json
import boto3
import os

def lambda_handler(event, context):
    my_region = os.environ['AWS_REGION']
    dynamoDBTableName = os.environ['dynamoDBTableName']
    dynamodb = boto3.resource('dynamodb', region_name=my_region)
    table = dynamodb.Table(dynamoDBTableName)
    raw_kinesis_records = event['Records']
    if event['isFinalInvokeForWindow']:

        item = {
            'windowEnd': event["window"]["end"],
            'windowStart': event["window"]["start"],
            'passenger': event["state"]["passengerCount"],
            'vendorId': event["state"]["vendorId"]
        }
        # Store to dynamoDB Table
        ddb_data = json.loads(json.dumps(item), parse_float=Decimal)
        #print ( "ddb_data", ddb_data)
        response = table.put_item(
            Item=ddb_data
        )
        print ('response' ,response)
    else:
        print('Aggregate invoke')

    #Check for early terminations
    if event['isWindowTerminatedEarly']:
        print('Window terminated early')
    #Aggregation logic

    if (str(event["state"])) == "{}":
        stateJson = {"state":{"passengerCount":0}}
        event.update(stateJson)

    state = event['state']
    # Deaggregate all records in one call
    user_records = deaggregate_records(raw_kinesis_records)
    
    # Iterate through deaggregated records
    for record in user_records:
        payload=base64.b64decode(record["kinesis"]["data"]).decode("UTF-8")
        #print("Decoded payload: " + str(payload))
        formattedPayload = json.loads(payload)
        #p = str(payload)
        if "passengerCount" in formattedPayload:
         value = formattedPayload["passengerCount"]
         state['passengerCount'] += value
         state['vendorId'] = formattedPayload['vendorId']

    return {'state': state}

