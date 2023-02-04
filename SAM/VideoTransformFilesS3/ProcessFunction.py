import json
import boto3

def lambda_handler(event, context):
    if len(event['Records']) != 1:
        raise ValueError('Error format message')
    
    s3 = boto3.client('s3')
    bucket_name = event['Records'][0]['messageAttributes']['BucketName']['stringValue']
    key_file = event['Records'][0]['messageAttributes']['FileName']['stringValue']
    bytes_range = event['Records'][0]['body']
    resp = s3.get_object(Bucket=bucket_name, Key=key_file, Range=bytes_range)
    data = resp['Body'].read()
    print(type(data))
    
    return {
        'statusCode': 200,
        'body': json.dumps("Ok")
    }