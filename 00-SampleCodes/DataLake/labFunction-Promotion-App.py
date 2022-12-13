import os
import logging
import boto3
from botocore.exceptions import ClientError

import pandas as pd
from collections import defaultdict

inputBucket = os.environ['input_bucket']
outputBucket = os.environ['output_bucket']

def lambda_handler(event, context):
    download_file(file_name='cart_abandonment_data.csv', bucket=inputBucket)
    process_file(file_name='cart_abandonment_data.csv')
    upload_file(file_name='/tmp/promotion_data.csv',bucket=outputBucket)
    
def download_file(file_name, bucket, object_name=None):
    s3 = boto3.client('s3')
    s3.download_file(bucket, file_name, '/tmp/' + file_name)

def process_file(file_name):
    raw_data = pd.read_csv('/tmp/'+file_name)
    aggregate_data = raw_data.groupby(['customer_id','product_id']).agg({'product_amount':sum})
    group_data = aggregate_data['product_amount'].groupby('customer_id', group_keys=False).nlargest(10)
    print(group_data.head(15))
    group_data.to_csv('/tmp/promotion_data.csv')

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True
