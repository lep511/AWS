import boto3
import uuid
import json
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TABLE_NAME = os.environ['TABLE_NAME']

client = boto3.resource('dynamodb')
table = client.Table(TABLE_NAME)

def lambda_handler(event, context):
    json_event = json.dumps(event)
    print("--event: " + json_event)
    
    for record in event['Records']:
        payload = record["body"]
        logger.info("Payload: " + str(payload))
        table.put_item(Item= {'orderID': str(uuid.uuid4()),'order':  payload})