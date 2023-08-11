import boto3
import os
from botocore.exceptions import ClientError

def add_donation(item):
    dynamo = boto3.client('dynamodb')
    table = os.environ['DYNAMODB_TABLE']
    try:
        response = dynamo.update_item(
            TableName=table,
            Key={'id': item['id']},
            UpdateExpression="set donation = donation + :val",
            ExpressionAttributeValues={':val': {'N': item['donation']['N']}}
        )
        if  response['ResponseMetadata']['HTTPStatusCode'] == 200:
            message_code = "Success update item"
    except  ClientError as e:
        print("[ERROR]", e.response['Error']['Message'])
        message_code = "Error update item"

    return message_code