import os
import json
import boto3
import botocore.exceptions

def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }