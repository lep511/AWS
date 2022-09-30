import boto3
import json
import time

# Boto3 - DynamoDB Client - Mode Info: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html
sqs = boto3.resource('sqs')

# Replace Queue name with Queue URL from Account
queue = sqs.Queue('https://sqs.us-east-1.amazonaws.com/311925530315/MyMessageQueue')

# AWS Lambda Function that publishes a message at Queue
def lambda_handler(event, context):

    message = {
        "coder_id": "123",
        "spot_id": "321",
        "timestamp": round(time.time() * 1000)
    }
    response = queue.send_message(MessageBody=json.dumps(message))

    return response
