import json
import boto3
from botocore.exceptions import ClientError
import os

def lambda_handler(event, context):
    if event:
        print(event)
        dynamo = boto3.client('dynamodb')
        sqs = boto3.client('sqs')
        sqs_queue_url = os.environ['SQS_QUEUE_URL']
        table = os.environ['DYNAMODB_TABLE']
        tot_items = len(event['Records'])
        sqs_batch_response = {}
        batch_item_failures = []
        update_item = []

        print(f"Total items in SQS: {tot_items}")
        # Write elements from SQS to Dynamo
        for record in event['Records']:
            body = json.loads(record['body'])
            item = {
                'id': {'S': body['email']},
                'name': {'S': body['name']},
                'donation': {'N' : str(body['donation'])}
            }
            try:
                # Put item in DynamoDB if it does not exist
                dynamo.put_item(
                    TableName=table,
                    Item=item,
                    ConditionExpression="attribute_not_exists(id)"
                )
            except ClientError as e:
                if e.response['Error']['Code'] == "ConditionalCheckFailedException":
                    response = add_donation(item)
                    update_item.append({"updateReport": response})
                else:
                    batch_item_failures.append({"itemIdentifier": record['messageId']})
                    print("[ERROR]", e.response['Error']['Message'])

            else:
                # Delete message from SQS
                sqs.delete_message(
                    QueueUrl=sqs_queue_url,
                    ReceiptHandle=record['receiptHandle']
                )

        sqs_batch_response["batchItemFailures"] = batch_item_failures
        sqs_batch_response["updateItem"] = update_item
        return sqs_batch_response

    return {
        'statusCode': 200
    }

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