import json
import boto3
import uuid
from datetime import date
import random

def lambda_handler(event, context):
    client = boto3.client('sns')
    
    message = {
            'CustomerId': str(uuid.uuid4()),
            'DateOrderId': str(date.today()),
            'PaymentAmount': int(random.randint(1, 30400))
    }
    
    
    response = client.publish(
        TargetArn='arn:aws:sns:us-east-1:432756446153:new_topic',
        Message=json.dumps({'default': json.dumps(message)}),
        MessageStructure='json'
    )
    print(response)
    return {
        'statusCode': 200,
        'body': json.dumps('Message published!')
    }