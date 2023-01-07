import json
import logging
import os
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        logger.info('Event: {}'.format(event))
        logger.info('Context: {}'.format(str(context)))

        table_name = os.getenv('DDB_TABLE')
        if (not table_name):
            raise Exception('Table name missing') 
        
        dynamodb = boto3.resource('dynamodb')
        ddb_table = dynamodb.Table(table_name)

        items = ddb_table.scan()

        logger.info('DDB Response: {}'.format(items))

        if ('Items' in items):
            response = {
                'statusCode': 200,
                'body': json.dumps(items['Items'])
            }
        else:
            response = {
                'statusCode': items['HTTPStatusCode']
            }
        
        logger.info("Response: %s", response)

        return response
    except Exception as error:
        logger.info('Error: {}'.format(error))
        return {
            'statusCode': 500,
            'body': {'message': error}
        }
