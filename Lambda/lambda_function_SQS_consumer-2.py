import json
import boto3

# Boto3 - DynamoDB Client - Mode Info: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html
dynamodb = boto3.resource('dynamodb')

# AWS Lambda Function that consumes event from Queue and writes at DynamoDB
def lambda_handler(event, context):
    if 'Records' in event:
        for record in event['Records']:
            payload = json.loads(record["body"])
            if 'id' not in payload:
                raise ValueError('error format')
            else:
                table = dynamodb.Table('http-crud-tutorial-items')
                payload_rest = payload.copy()
                payload_rest.pop("id")
                item = {'id': payload['id'], **payload_rest}
                table.put_item(
                   Item=item
                )

    return {
        'statusCode': 200,
        'body': json.dumps(payload)
    }

