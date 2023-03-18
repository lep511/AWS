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

        try:
            payload = json.loads(event['body'])
        except Exception as error:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Bad Request'})
            }

        if ('title' not in payload and 'completed' not in payload and 'description' not in payload):
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Nothing to update'})
            }

        item = ddb_table.update_item(
            Key={
                'id': id
            },
            ExpressionAttributeValues=buildAttributeValues(payload),
            UpdateExpression=buildUpdateExpression(payload),
            ReturnValues='ALL_NEW'
        )

        logger.info('DDB Response: {}'.format(item))

        if ('Attributes' in item):
            response = {
                'statusCode': 200,
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
            'body': {'message': 'Internal Server Error'}
        }


def buildUpdateExpression(payload):
    updateExpression = 'set '
    if ('title' in payload):
        updateExpression += 'title = :t, '
    if ('completed' in payload):
        updateExpression += 'completed = :c, '
    if ('description' in payload):
        updateExpression += 'description = :d, '
    return updateExpression[:-2]


def buildAttributeValues(payload):
    attributes = {}
    if ('title' in payload):
        attributes[':t'] = payload['title']
    if ('completed' in payload):
        attributes[':c'] = payload['completed']
    if ('description' in payload):
        attributes[':d'] = payload['description']
    return attributes
