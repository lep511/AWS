import boto3
from boto3.dynamodb.conditions import Key, Attr
import json

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('SuperMissionTable')

    condition = {}
    condition["SuperHero"] = event["superhero"]

    response = table.query(KeyConditionExpression=Key("SuperHero").eq(condition["SuperHero"]))
    return response
