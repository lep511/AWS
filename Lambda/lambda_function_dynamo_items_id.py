#Lambda function in python to get an item in dynamodb by key

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

    id = event['pathParameters']['id']
    logger.info(id)


    #get the item from the table using id
    item = table.get_item(Key={'id': id})

   
    #html formatted response with header and body
    response = {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET,OPTIONS,POST'
        },
        'body': json.dumps(item['Item'])
    }
    
    logger.info(response)
    return response