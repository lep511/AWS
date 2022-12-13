import boto3
import json
import os
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('TABLENAME'))
management = boto3.client('apigatewaymanagementapi', endpoint_url=os.getenv('APIGW_ENDPOINT'))

def lambda_handler(event, context):
  try:
    response = table.get_item(
      Key={
      'order_id': event["detail"]['item']['order_id']
      }
    )
    management.post_to_connection(
      Data=json.dumps(event["detail"]),
      ConnectionId=response["Item"]["connection_id"]
    )
  except ClientError as err:
    print(err)

