import boto3
import json
import os
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('TABLENAME'))

def lambda_handler(event, context):
  try:
    order_id=event['queryStringParameters']['order_id']
    response = table.put_item(
      Item={
      'order_id': order_id,
      'connection_id': event["requestContext"]["connectionId"]
      })

    return {
      "statusCode": 200,
      "headers": {
      "Content-Type": "application/json"
    }
    }
  except ClientError as err:
    print(err)
