import json
import boto3

# Boto3 - DynamoDB Client - Mode Info: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html
sqs = boto3.resource('sqs')
dynamodb = boto3.resource('dynamodb')

# AWS Lambda Function that consumes event from Queue and writes at DynamoDB
def lambda_handler(event, context):
    if 'Records' in event:
        for record in event['Records']:
            payload = json.loads(record["body"])
            if 'coder_id' not in payload:
                raise ValueError('erro format')
            else:
                table = dynamodb.Table('checkinData')
                table.put_item(
                   Item={
                        'coderId': payload['coder_id'],
                        'timestamp': payload['timestamp'],
                        'spotID': payload['spot_id']
                        }
                )

    return {
        'statusCode': 200,
        'body': json.dumps(payload)
    }