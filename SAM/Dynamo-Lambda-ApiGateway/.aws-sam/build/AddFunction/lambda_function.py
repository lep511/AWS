import json
import logging
import os
import datetime
import boto3
import uuid

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        logger.info('Event: {}'.format(event))
        logger.info('Context: {}'.format(context))

        table_name = os.getenv('DDB_TABLE')
        if (not table_name):
            raise Exception('Table name missing') 

        dynamodb = boto3.resource('dynamodb')
        ddb_table = dynamodb.Table(table_name)

        try:
            payload = json.loads(event['body'])
        except Exception as error:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Bad Request'})
            }

        if ('title' not in payload):
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Title missing'})
            }
        
        description = '' if 'description' not in payload else payload['description']

        todo = {
            'id': uuid.uuid4().hex,
            'completed': False,
            'created_at': datetime.datetime.now().isoformat(),
            'title': payload['title'],
            'description': description
        }

        ddb_response = ddb_table.put_item(
            Item=todo
        )

        logger.info('DDB Response: {}'.format(ddb_response))

        response = {
            'statusCode': 201,
            'body': json.dumps(todo)
        }
        logger.info("Response: %s", response)

        return response

    except Exception as error: 
        logger.info('Error: {}'.format(error))
        return {
            'statusCode': 500,
            'body': {'message': error}
        }
