import json
import os
import boto3
import logging

event_bus_name = os.environ['EVENT_BUS_NAME']
logger = logging.getLogger()
logger.setLevel(logging.INFO)

print('Loading function')

#Updates an SSM parameter
#Expects parameterName, parameterValue
def lambda_handler(event, context):
    json_event = json.dumps(event)
    print("--event: " + json_event)

    # get SSM client
    client = boto3.client('ssm')
    eventbridge = boto3.client('events')
    parameterName = event['detail']['name']
    
    # Get the parameter store value
    response = client.get_parameter(
        Name=parameterName,
        WithDecryption=False
    )
    data_value = response["Parameter"]["Value"]
    
    # Send the event to EventBridge
    response = eventbridge.put_events(
        Entries=[
            {   
                'EventBusName': event_bus_name,
                'Source': 'my.statemachine',
                'DetailType': 'MessageFromStepFunctions',
                'Detail': json.dumps({
                    'Message': data_value
                })
            }
        ]
    )
    if response["FailedEntryCount"] > 0:
        msg = "Failed to send event to EventBridge"
        logger.error(msg)
        logger.error(response)
        return {"statusCode": 400, "body": json.dumps({"message": msg})}
    
    return {"statusCode": 200, "body": json.dumps({"message": "Success"})}
