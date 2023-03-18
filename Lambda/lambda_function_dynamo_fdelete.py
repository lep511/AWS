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
        
        try:
            id = event['pathParameters']['id']
        except Exception as error:
            logger.info('Error: {}'.format(error))
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Bad Request'})
            }
        
        dynamodb = boto3.resource('dynamodb')
        ddb_table = dynamodb.Table(table_name)

        item = ddb_table.delete_item(
            Key={
                'id': id
            }
        )

        logger.info('DDB Response: {}'.format(item))

        if ('Attributes' in item):
            response = {
                'statusCode': 204,
                'body': json.dumps(item['Attributes'])
            }
        else:
            response = {
                'statusCode': item['ResponseMetadata']['HTTPStatusCode']
            }
        
        logger.info("Response: %s", response)

        return response
    except Exception as error:
        logger.info('Error: {}'.format(error))
        return {
            'statusCode': 500,
            'body': {'message': error}
        }
