import os
import json
import logging
import boto3
from botocore.vendored import requests


logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client('lambda')
client.get_account_settings()

def lambda_handler(event, context):
    json_event = json.dumps(event)
    print("[EVENT] " + json_event)
    
    r = requests.get('https://httpbin.org/basic-auth/user/pass', auth=('user', 'pass'))
    print(f"Status code: {r.status_code}")

    return r.json()