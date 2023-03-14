from decimal import Decimal
import base64
import json
import boto3
from botocore.exceptions import ClientError
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info('## RECORDS COUNT')
    logger.info(len(event["Records"]))
    my_region = os.environ['AWS_REGION']
    dynamoDBTableName = os.environ['dynamoDBTableName']
    dynamodb = boto3.resource('dynamodb', region_name=my_region)
    table = dynamodb.Table(dynamoDBTableName)
    state = json.dumps("")
    all_items = []

    for elem in event["Records"]:
        raw_kinesis_records = elem['kinesis']['data']
        payload=str(base64.b64decode(raw_kinesis_records).decode("UTF-8"))
        formattedPayload = json.loads(payload)
        #print(formattedPayload)
        ddb_data = json.loads(payload, parse_float=Decimal)
        all_items.append(ddb_data)

    try:
        with table.batch_writer() as writer:
            for item in all_items:
                writer.put_item(Item=item)
    except ClientError as err:
            logger.error(
                "Couldn't load data into table %s. Here's why: %s: %s", table.name,
                err.response['Error']['Code'], err.response['Error']['Message'])
            status_code = 400
    else:
        status_code = 200
        
    return {
        "statusCode": status_code
    }
