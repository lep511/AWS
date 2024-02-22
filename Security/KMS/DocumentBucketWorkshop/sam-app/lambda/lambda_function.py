"""
{
  "source": ["aws.s3"],
  "detail-type": ["Object Created"],
  "detail": {
    "bucket": {
      "name": ["data-bucket-4939-23"]
    },
    "object": {
      "key": [{
        "prefix": "logs/metadata/"
      }]
    }
  }
}
"""

import boto3
import json
from botocore.exceptions import ClientError
import os

dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')
s3 = boto3.resource('s3')
table_name = os.getenv('DDB_TABLE')

def lambda_handler(event, handler):
    if table_name is None:
      raise Exception("DDB_TABLE environment variable not set")
    else:
      table = dynamodb.Table(table_name)
    
    bucket_name = event['detail']['bucket']['name']
    file_event = event['detail']['object']['key']
    file = s3.Object(bucket_name, file_event)
    file = file.get()['Body'].read().decode('utf-8')

    all_data = file.split('\n')[:-1]
    count = 0
    
    for reg in all_data:
        json_reg = json.loads(reg)
        file_name = json_reg['output'].split('/')[-1]

        try:
            response = s3_client.head_object(Bucket=bucket_name, 
                                                Key=f'logs/{file_name}', 
                                                Range='bytes=0-0'
                                            )
        except ClientError as e:
            if e.response['Error']['Code'] == "404":
                print(f"The object does not exist: {file_name}")
            else:
                print(f"[ERROR] Loading: {file_name}")
        else:
            # Put item in dynamodb table
            pk = file_event.split('/')[-1]
            sk = json_reg['output'].split('/')[-1]
            try:
                table.put_item(
                    Item={
                        'pk': pk,
                        'sk': sk,
                        'metadata': json_reg
                    }   
                )
            except ClientError as e:
                print(f"[ERROR] Writing to dynamodb: {file_name}")
                print(e.response['Error']['Message'])
            else:
                count += 1
                
    print("Total files processed:", count, "| Total files not processed:", len(all_data) - count)
    
    return {
        'statusCode': 200
    }