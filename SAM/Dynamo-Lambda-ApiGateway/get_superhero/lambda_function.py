import boto3
from boto3.dynamodb.conditions import Key
import json

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('SuperMissionTable')
    superhero = event['pathParameters']['SuperHero']

    response = table.query(KeyConditionExpression=Key("SuperHero").eq(superhero))
    return {
        'statusCode': 200,
        'body': json.dumps(response['Items'])
    }