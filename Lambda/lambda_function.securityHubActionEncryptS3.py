import boto3
import sys
import re
import string
import random
import json
import os
kkID=os.environ['KMS_KEY_ID']
s3c = boto3.client('s3')
def handler(event, context):
    bkArn = (event['detail']['findings'][0]['Resources'][0]['Id']).split(":")
    bkN = bkArn[5]
    response = s3c.put_bucket_encryption(
            Bucket = bkN,
            ServerSideEncryptionConfiguration={
                'Rules': [
                    {
                        'ApplyServerSideEncryptionByDefault': {
                            'SSEAlgorithm': 'aws:kms',
                            'KMSMasterKeyID': kkID
                        }
                    }
                ]
            }    
    )
