import boto3
import json
from decimal import *

dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    table = dynamodb.Table('http-crud-tutorial-items')
    print(event)

    if event['routeKey'] == 'DELETE /items/{id}':
        table.delete_item(
            Key={
                'id': event['pathParameters']['id']
            }
        )

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps('Deleted item {}'.format(event['pathParameters']['id']), cls=DecimalEncoder)
        }

    elif event['routeKey'] == 'GET /items/{id}':
        try:
            result = table.get_item(
            Key={
                    'id': event['pathParameters']['id']
                }
            )

            return {
                'statusCode': 200,
                'headers': {
                'Content-Type': 'application/json'
                },
                'body': json.dumps(result['Item'], cls=DecimalEncoder)
            }
        except:
            return {
                'statusCode': 400,
                'body': json.dumps('Items not found')
            }

    elif event['routeKey'] == 'GET /items':
        result = table.scan()

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps(result['Items'], cls=DecimalEncoder)
        }

    elif event['routeKey'] == 'PUT /items':
        requestJSON = json.loads(event['body'])

        table.put_item(
            Item={
                'id': requestJSON['id'],
                'price': requestJSON['price'],
                'name': requestJSON['name']
            }
        )

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps('Put item {}'.format(requestJSON['id']), cls=DecimalEncoder)
        }

    else:
        return {
            'statusCode': 400,
            'body': json.dumps('Unsupported route: {}'.format(event['routeKey']), cls=DecimalEncoder)
        }
    


############################################################################################################
# This class is used to convert the Decimal type to a float type so that it can be serialized by json.dumps
############################################################################################################

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        # convert it to a string
        if isinstance(obj, Decimal):
            return str(obj)
        return json.JSONEncoder.default(self, obj)