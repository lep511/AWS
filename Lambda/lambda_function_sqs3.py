import json
import boto3
import os

def lambda_handler(event, context):
    QUEUE_URL = os.environ['queue_url']
    
    # sqs client
    client = boto3.client('sqs')
    
    receiveMessage = client.receive_message(
        QueueUrl=QUEUE_URL,
        MaxNumberOfMessages=10,
        WaitTimeSeconds=5
    )
    
    for m in receiveMessage.get('Messages', []):

        print(m)
        
        receipt_handle = m['ReceiptHandle']
        client.delete_message(
            QueueUrl=QUEUE_URL,
            ReceiptHandle=receipt_handle
        )
    
    processed_messages = len(receiveMessage.get('Messages', []))
    
    if processed_messages == 0:
        message = 'No messages found in queue. Messages processed: ' + str(processed_messages)
    else:
        message = 'Messages processed: ' + str(processed_messages)
        
    return {
        'statusCode': 200,
        'body': json.dumps(message)
    }