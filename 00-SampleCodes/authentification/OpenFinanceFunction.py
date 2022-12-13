"""
This lambda function performs CRUD againstDynamoDb.
"""

import json
import sys
import os
import boto3
from botocore.exceptions import ClientError
import logging

dynamodb_client = boto3.client('dynamodb')
dynamodb_resource = boto3.resource('dynamodb')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(json.dumps(event))
    
    print(event['httpMethod'])
    print(event['resource'])
    try:
        if event['httpMethod'] == 'GET' and event['resource'] == '/items':
            logger.info('GET method - Scan table')
            response_scan = dynamodb_client.scan(TableName='bank-data')
            data = response_scan['Items']
            logger.info(json.dumps(response_scan['Items']))
            
            return_response = {
                'statusCode': 200,
                'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(data),
                "isBase64Encoded": False
            }
            return return_response
            
        elif event['httpMethod'] == 'GET' and event['resource'] == "/items/{id}":
            logger.info('GET method - query table')
            try:
                id_val = event['path'].split('/')[2]
            except exceptions as e:
        
                id_val = event['queryStringParameters']['id']
            logger.info(id_val)
            table = dynamodb_resource.Table('bank-data')
            response_query = table.get_item(
                        Key={
                          'id': id_val
                        })
            logger.info(response_query)
            data = response_query['Item']
            return_response = {
                'statusCode': 200,
                'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(data),
                "isBase64Encoded": False
            }
            return return_response
        else:
            logger.info(f'Something went wrong')
    except Exception as e:
        logger.info(f'Error: {e}')