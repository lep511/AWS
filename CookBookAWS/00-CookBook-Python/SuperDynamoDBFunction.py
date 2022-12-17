import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('SuperMissionTable')

def lambda_handler(event, context):
    response = table.scan()
    return response['Items']
