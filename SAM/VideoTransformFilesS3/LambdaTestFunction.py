import json
import boto3
import math

queue_url = 'https://sqs.us-east-1.amazonaws.com/282495905450/FileDataQueue'

def lambda_handler(event, context):
    print(event)
    sqs = boto3.client('sqs')
    bucket_name = event['bucket_name']
    object_name = event['file_name']
    part_size = 32 * 1024 * 1024 # 32 MB chunk size

    file_size = event['file_size']
    
    byte_start = 0
    byte_finish = part_size
    for i in range(round_up(file_size / part_size)):
        text_body = f"bytes={byte_start}-{byte_finish}"
        send_sqs(sqs, text_body, bucket_name, object_name)
        byte_start += part_size + 1
        byte_finish += part_size + 1
        if byte_finish > file_size:
            byte_finish = file_size
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

def round_up(n, decimals=0):
    multiplier = 10 ** decimals
    return int(math.ceil(n * multiplier) / multiplier)

def send_sqs(client, text_body, bucket_name, object_name):
    response = client.send_message(
        QueueUrl=queue_url,
        DelaySeconds=0,
        MessageAttributes={
            'FileName': {
                'DataType': 'String',
                'StringValue': object_name
            },
            'BucketName': {
                'DataType': 'String',
                'StringValue': bucket_name
            }
        },
        MessageBody=(text_body)
    )
