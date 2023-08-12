import json
import boto3
import os
from botocore.exceptions import ClientError

import os

def lambda_handler(event, context):
    if event:
        dynamo = boto3.client('dynamodb')
        sqs = boto3.client('sqs')
        sqs_queue_url = os.environ['SQS_QUEUE_URL']
        sqs_queue_arn = os.environ['SQS_QUEUE_ARN']
        dlq_arn = os.environ['DLQ_ARN']
        table = os.environ['DYNAMODB_TABLE']
        tot_items = len(event['Records'])
        batch_item_failures = []

        # Write elements from SQS to Dynamo
        for record in event['Records']:
            body = json.loads(record['body'])
            message_id = record["messageId"]
            
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
                    if is_duplicate_message(message_id):   
                        print("Message duplicate: " + message_id)
                        delete_sqs_message(record['receiptHandle'])
                    else:
                        # Sum donation to existing item
                        check_item = add_donation(item, message_id)
                        if not check_item:
                            batch_item_failures.append({"itemIdentifier": message_id})
                            print(f"[ERROR][A01] Cannot add donation to item {item['id']['S']}")
                else:
                    batch_item_failures.append({"itemIdentifier": message_id})
                    print("[ERROR][A02]", e.response['Error']['Message'])

            else:
                # Delete message from SQS
                delete_sqs_message(record['receiptHandle'])
                # Add message to processed records table
                push_to_process_table(message_id)

        tot_items_fail = len(batch_item_failures)
        
        if tot_items_fail > 0:
            raise Exception(f"Error processing {tot_items_fail} items out of {tot_items}")
        else:
            print(f"Total items in SQS: {tot_items} - Total items failed: {tot_items_fail}")
            return {
                'statusCode': 200
            }
        

def is_duplicate_message(message_id):
    dynamo = boto3.client('dynamodb')
    table_name = os.environ['PROCESSED_RECORDS']
    return dynamo.query(
        TableName=table_name,
        Select='COUNT',
        KeyConditionExpression='Records = :Records',
        ExpressionAttributeValues={
            ':Records': {'S': message_id}
        }
    )["Count"] != 0
    

def add_donation(item, message_id):
    dynamo = boto3.client('dynamodb')
    table = os.environ['DYNAMODB_TABLE']
    try:
        response = dynamo.update_item(
            TableName=table,
            Key={'id': item['id']},
            UpdateExpression="set donation = donation + :val",
            ExpressionAttributeValues={':val': {'N': item['donation']['N']}}
        )
        if  response['ResponseMetadata']['HTTPStatusCode'] != 200:
            return False

    except  ClientError as e:
        print("[ERROR][A03]", e.response['Error']['Message'])
        return False
    
    else:
        push_to_process_table(message_id)

    return True


def push_to_process_table(message_id):
    dynamo = boto3.client('dynamodb')
    table_name = os.environ['PROCESSED_RECORDS']
    try:
        response = dynamo.put_item(
                    TableName = table_name, 
                    Item={ 'Records': {'S':message_id}
                    }
                )
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            print(f"[ERROR][A04] {response}")

    except ClientError as e:
        print("[ERROR][A05]", e.response['Error']['Message'])


def delete_sqs_message(receipt_handle):
    sqs = boto3.client('sqs')
    sqs_queue_url = os.environ['SQS_QUEUE_URL']
    try:
        sqs.delete_message(
            QueueUrl=sqs_queue_url,
            ReceiptHandle=receipt_handle
        )
    except ClientError as e:
        print("[ERROR][A06]", e.response['Error']['Message'])