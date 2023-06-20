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
    s3_client = boto3.client('s3')
    
    record_count = len(event["Records"])
    logger.info(f'## RECORDS COUNT: {record_count}')

    all_data = check_insert_data(event['Records'])
    df = pd.DataFrame(all_data)
    
    now_date = datetime.now()
    year = now_date.strftime("%Y")
    month = now_date.strftime("%m")
    day = now_date.strftime("%d")
    # Unix time
    unix_time = time.time()
    file_name = f'retailcart-events-{unix_time}.parquet'

    try:
        # Save df to parquet in s3
        df.to_parquet(f'/tmp/{file_name}')
        s3_client.upload_file(f'/tmp/{file_name}', bucket_name, f'retail-cart-data/{year}/{month}/{day}/{file_name}')
        logger.info('## SAVED TO S3')
    
    except Exception as e:
        logger.error(f'## ERROR: {e}')
        status_code = 400

    return {
        "statusCode": status_code
    }


def check_insert_data(records):
    all_process_items = []
    
    for elem in records:
        raw_kinesis_records = elem['kinesis']['data']
        payload=str(base64.b64decode(raw_kinesis_records).decode("UTF-8"))
        formattedPayload = json.loads(payload)
        ddb_data = json.loads(payload, parse_float=Decimal)
        # ------------------------------------------------------
        # PURCHASE EVENT
        # ------------------------------------------------------
        if ddb_data['eventName'] == 'INSERT' and ddb_data['dynamodb']['NewImage']['Status']['S'] == 'PURCHASED':
            item = dict()
            item['eventId'] = ddb_data['eventID']
            item['createTimestamp'] = ddb_data['dynamodb']['NewImage']['CreateTimestamp']['S']
            item['productId'] = ddb_data['dynamodb']['NewImage']['ItemSKU']['M']['ProductId']['S']
            item['price'] = float(ddb_data['dynamodb']['NewImage']['ItemSKU']['M']['Price']['N'])
            item['quantity'] = int(ddb_data['dynamodb']['NewImage']['ItemSKU']['M']['Quantity']['N'])
            item['status'] = ddb_data['dynamodb']['NewImage']['Status']['S']
            all_process_items.append(item)

        # ------------------------------------------------------
        # SAVED EVENT
        # ------------------------------------------------------
        elif ddb_data['eventName'] == 'INSERT' and ddb_data['dynamodb']['NewImage']['Status']['S'] == 'SAVED':
            item = dict()
            item['eventId'] = ddb_data['eventID']
            item['createTimestamp'] = ddb_data['dynamodb']['NewImage']['CreateTimestamp']['S']
            item['productId'] = ddb_data['dynamodb']['NewImage']['ItemSKU']['M']['ProductId']['S']
            item['price'] = None
            item['quantity'] = None
            item['status'] = ddb_data['dynamodb']['NewImage']['Status']['S']
            all_process_items.append(item)
        # ------------------------------------------------------
        # ACTIVE EVENT
        # ------------------------------------------------------
        elif ddb_data['eventName'] == 'INSERT' and ddb_data['dynamodb']['NewImage']['Status']['S'] == 'ACTIVE':
            item = dict()
            item['eventId'] = ddb_data['eventID']
            item['createTimestamp'] = ddb_data['dynamodb']['NewImage']['CreateTimestamp']['S']
            item['productId'] = ddb_data['dynamodb']['NewImage']['ItemSKU']['M']['ProductId']['S']
            item['price'] = float(ddb_data['dynamodb']['NewImage']['ItemSKU']['M']['Price']['N'])
            item['quantity'] = int(ddb_data['dynamodb']['NewImage']['ItemSKU']['M']['Quantity']['N'])
            item['status'] = ddb_data['dynamodb']['NewImage']['Status']['S']
            all_process_items.append(item)
        # ------------------------------------------------------
        # REMOVED EVENT
        # ------------------------------------------------------
        elif ddb_data['eventName'] == 'REMOVE':
            item = dict()
            item['eventId'] = ddb_data['eventID']
            item['createTimestamp'] = ddb_data['dynamodb']['NewImage']['CreateTimestamp']['S']
            item['productId'] = ddb_data['dynamodb']['NewImage']['ItemSKU']['M']['ProductId']['S']
            # Check if price and quantity exists
            if 'Price' in ddb_data['dynamodb']['NewImage']['ItemSKU']['M']:
                item['price'] = float(ddb_data['dynamodb']['NewImage']['ItemSKU']['M']['Price']['N'])
            else:
                item['price'] = None

            if 'Quantity' in ddb_data['dynamodb']['NewImage']['ItemSKU']['M']:
                item['quantity'] = int(ddb_data['dynamodb']['NewImage']['ItemSKU']['M']['Quantity']['N'])
            else:           
                item['quantity'] = None
            item['status'] = 'REMOVED'
            all_process_items.append(item)
    
    return all_process_items