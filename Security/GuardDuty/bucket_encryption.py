import boto3
import json
import logging

logger = logging.getLogger()

# Check the bucket encryption status

s3 = boto3.client('s3')

def check_encryption(bucket_name):
    response = s3.get_bucket_encryption(Bucket=bucket_name)
    logger.info(json.dumps(response, indent=4, sort_keys=True, default=str))
    if response['ServerSideEncryptionConfiguration']['Rules'][0]['ApplyServerSideEncryptionByDefault']['SSEAlgorithm'] == 'AES256':
        print('Bucket encryption is enabled')
        return True
    else:
        print('Bucket encryption is not enabled')
        return False
