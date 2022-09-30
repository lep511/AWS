from __future__ import print_function
import boto3
from datetime import datetime
import json

dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    table = dynamodb.Table("MessagesTable")
    
    for record in event['Records']:
        print("test")
        payload = json.loads(record["body"])
        print(payload)
        response = table.put_item(
            Item={
                'MessagesId': payload["messageId"],
                'Body': payload["body"],
                'Timestamp': datetime.now().isoformat()
            }
        )
        print(response)
    