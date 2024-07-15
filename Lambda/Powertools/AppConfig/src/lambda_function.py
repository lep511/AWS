import boto3
import json
from pydantic import BaseModel, create_model
from typing import Any
import os

from aws_lambda_powertools.utilities.feature_flags import AppConfigStore, FeatureFlags
from aws_lambda_powertools.utilities.typing import LambdaContext

DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE']
app_config = AppConfigStore(environment="dev", application="comments", name="config")
feature_flags = FeatureFlags(store=app_config)

dynamo = boto3.client('dynamodb')

def lambda_handler(event, context):
    print(event)
    apply_discount: Any = feature_flags.evaluate(name="ten_percent_off_campaign", default=False)
    price: Any = event.get("price")
    
    if apply_discount:
        # apply 10% discount to product
        price = price * 0.9
    
    operations = {
        'DELETE': lambda dynamo, x: dynamo.delete_item(**x),
        'GET': lambda dynamo, x: dynamo.scan(**x),
        'POST': lambda dynamo, x: dynamo.put_item(**x),
        'PUT': lambda dynamo, x: dynamo.update_item(**x),
    }

    operation = event['httpMethod']
    print(operation)
    if operation in operations:
        payload = event['queryStringParameters'] if operation == 'GET' else json.loads(event['body'])
        return respond(None, operations[operation](dynamo, payload))
    else:
        return respond(ValueError('Unsupported method "{}"'.format(operation)))
    
    
def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }

