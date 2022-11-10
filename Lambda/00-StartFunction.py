import os
import json
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client('lambda')
client.get_account_settings()

def lambda_handler(event, context):
    json_event = json.dumps(event)
    print("[EVENT] " + json_event)
    
    json_context = json.dumps(context)
    print("[CONTEXT] " + json_context)

    response = client.get_account_settings()
    return response['AccountUsage']