import json
import boto3
from botocore.exceptions import ClientError
from check_duplicate import is_duplicate_message
from process_sqs import add_donation
from register_sqs import push_to_process_table

import os

def lambda_handler(event, context):
    if event:
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
                        response = "messageDuplicate"
                        batch_item_failures.append({response: message_id})
                    else:
                        # Sum donation to existing item
                        response = add_donation(item)
                        update_item.append({"updateReport": response})
                        # Add message to process table to avoid duplicates
                        resp_ptp = push_to_process_table(message_id)
                        if not resp_ptp:
                            print("[ERROR] Error pushing to process table:", message_id)
                    
                    if response != "Error update item":
                        # Delete message from SQS
                        sqs.delete_message(
                            QueueUrl=sqs_queue_url,
                            ReceiptHandle=record['receiptHandle']
                        )
                   
                else:
                    batch_item_failures.append({"itemIdentifier": message_id})
                    print("[ERROR]", e.response['Error']['Message'])

            else:
                # Delete message from SQS
                sqs.delete_message(
                    QueueUrl=sqs_queue_url,
                    ReceiptHandle=record['receiptHandle']
                )
                resp_ptp = push_to_process_table(message_id)
                if not resp_ptp:
                    print("[ERROR] Error pushing to process table:", message_id)                   

        sqs_batch_response["batchItemFailures"] = batch_item_failures
        sqs_batch_response["updateItem"] = update_item
        return sqs_batch_response

    return {
        'statusCode': 200
    }
