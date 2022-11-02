import boto3
import json
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SNS_ID = os.getenv('SNS_ID')

client = boto3.client('sns')

def lambda_handler(event, context):
    json_event = json.dumps(event)
    print("--event: " + json_event)
    
    for record in event["Records"]:

        if record['eventName'] == 'INSERT':
            logger.info("New order received")
            new_record = record['dynamodb']['NewImage']
            logger.info("New order: " + str(new_record))
            response = client.publish(
                TargetArn = SNS_ID,
                Message = json.dumps({'default': json.dumps(new_record)}),
                MessageStructure = 'json'
            )