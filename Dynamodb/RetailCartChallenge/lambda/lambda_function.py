import pandas as pd
from decimal import Decimal
import base64
import json
import boto3
from botocore.exceptions import ClientError
import os
import logging
from datetime import datetime
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    status_code = 200
    bucket_name = os.environ['bucketName']
    record_count = len(event["Records"])
    logger.info(f'## RECORDS COUNT: {record_count}')

    dm = check_insert_data(event['Records'])
    if dm:
        df = pd.DataFrame(dm)
        print(df)
        # Save df to parquet in s3
        now_date = datetime.now()
        year = now_date.strftime("%Y")
        month = now_date.strftime("%m")
        day = now_date.strftime("%d")
        # Unix time
        unix_time = time.time()
        file_name = f'purchase-events-{unix_time}.parquet'
        try:
            df.to_parquet(f's3://{bucket_name}/data/purchase/{year}/{month}/{day}/{file_name}')
            logger.info('## SAVED TO S3')
            status_code = 200
            logger.info(f'## STATUS CODE: {status_code}')
        except Exception as e:
            logger.error(f'## ERROR: {e}')
            status_code = 500
            logger.info(f'## STATUS CODE: {status_code}')
    else:
        logger.info('## NO INSERT EVENTS')
        status_code = 400
        logger.info(f'## STATUS CODE: {status_code}')
    
    return {
        "statusCode": status_code
    }

def check_insert_data(records):
    all_items = []
    for elem in records:
      raw_kinesis_records = elem['kinesis']['data']
      payload=str(base64.b64decode(raw_kinesis_records).decode("UTF-8"))
      formattedPayload = json.loads(payload)
      ddb_data = json.loads(payload, parse_float=Decimal)
      # ------------------------------------------------------
      # PURCHASE EVENT
      if ddb_data['eventName'] == 'INSERT' and ddb_data['dynamodb']['NewImage']['Status']['S'] == 'PURCHASED':
         item = dict()
         item['eventId'] = ddb_data['eventID']
         item['createTimestamp'] = ddb_data['dynamodb']['NewImage']['CreateTimestamp']['S']
         item['productId'] = ddb_data['dynamodb']['NewImage']['ItemSKU']['M']['ProductId']['S']
         all_items.append(item)
   return all_items