from typing import Dict

from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.streaming.s3_object import S3Object


def lambda_handler(event, context):
    bucket = event['BatchInput']['Bucket']
    
    for item in event['Items']:
        try:
            # Get file from S3
            key = item['Key']
            s3 = S3Object(bucket=bucket, key=key)
            for line in s3:
                print(line)

        except Exception as e:
            print(e)
            print('Error getting object {} from bucket {}.'.format(key, bucket))
            raise e
