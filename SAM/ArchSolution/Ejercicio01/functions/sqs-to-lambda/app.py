import boto3
import uuid
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.resource('dynamodb')
table = client.Table("orders")

def lambda_handler(event, context):
    logger.info('## EVENT')
    logger.info(event)
    
    for record in event['Records']:
        payload = record["body"]
        logger.info("Payload: " + str(payload))
        table.put_item(Item= {'orderID': str(uuid.uuid4()),'order':  payload})