import os
import boto3

def lambda_handler(event, context):
    
    s3_client = boto3.client(
      service_name='s3',
      endpoint_url='https://bucket.YOUR_VPC_INTERFACE_ENDPOINT_DNS'
      
    )
    

    #s3_client.list_buckets()
    # write to s3
    s3_client.put_object(Body=os.getenv('taskInfo'), Bucket=os.getenv('vpceBucket'), 
      Key=os.getenv('objectName'))
    # read from s3
    obj = s3_client.get_object(Bucket=os.getenv('vpceBucket'), Key=os.getenv('objectName'))
    body = obj['Body'].read()
    
    return {
    "Status": body.decode("utf-8")
    
    }