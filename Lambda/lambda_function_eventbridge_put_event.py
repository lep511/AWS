import json
import boto3
import os
from botocore.exceptions import ClientError

client = boto3.client('events')

def lambda_handler(event, context):
  try:
    detail = event["detail"]
    detail["item"]["eventtype"]="cook_pizza"
    response = client.put_events(
      Entries=[
        {
          'DetailType': 'eventtype',
          'Detail': json.dumps(detail),
          'EventBusName': os.environ.get('EVENT_BUS'),
          'Source':"make_pizza"
        },
      ]
    )
    print(response)
  except ClientError as err:
    print(err)
