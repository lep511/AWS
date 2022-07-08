import json
import boto3
from boto3.dynamodb.conditions import Key
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

table_name = "dragon_stats"

def lambda_handler(event, context):
    client = boto3.client('dynamodb')
    dragon_name = event.get('dragon_name_str')
    if dragon_name == None or dragon_name == "All":
        data = client.scan(
            TableName=table_name
        )
        response = data['Items']
    else:
        response = just_this_dragon(dragon_name)
    
    return response

def just_this_dragon(dragon_name):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    pk_name = table.key_schema[0]['AttributeName']
    data = table.query(
        KeyConditionExpression=Key(pk_name).eq(dragon_name)
    )
    return data['Items']
