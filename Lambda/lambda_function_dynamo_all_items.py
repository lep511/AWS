import boto3
import json
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

table_name = os.environ['SAMPLE_TABLE']

def lambda_handler(event, context):

    logger.info(event)
    if event['httpMethod'] != 'GET':
        return {
            'statusCode': 400,
            'body': json.dumps('Bad Request')
        }

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    items = table.scan()
    
    #html formatted response with header and body
    response = {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET,OPTIONS,POST'
        },
        'body': json.dumps(items["Items"])
    }
    
    logger.info(response)
    return response