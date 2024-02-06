import os
import json
import boto3
from operator import itemgetter

campaignArn = os.environ['CAMPAIGN_ARN']
personalizeRt = boto3.client('personalize-runtime')
dynamodb = boto3.resource('dynamodb')

car_table = dynamodb.Table('Car')

def get_personalize_recommendations(userId):
    response = personalizeRt.get_recommendations(
        campaignArn = campaignArn,
        userId = userId,
        numResults = 3
    )
    
    return response
    
def lambda_handler(event, context):
    userId = event['pathParameters']['id']
    response = get_personalize_recommendations(userId)
    car_list = response['itemList']
    print(userId)
    item_ids = []
    
    for car in car_list:
        item_ids.append(car['itemId'])
        
    batch_keys = {
        car_table.name: {
            'Keys': [{'id': car['itemId']} for car in car_list],
            'ProjectionExpression': 'id, #name, category, imageUrl',
            'ExpressionAttributeNames': {'#name': 'name'}
        }
    }
    
    response = dynamodb.batch_get_item(RequestItems=batch_keys)
    recommendations = response['Responses']['Car']
    
    for recommendation in recommendations:
        for car in car_list:
            if recommendation['id'] == car['itemId']:
                recommendation['score'] = car['score']
                
    recommendations = sorted(recommendations, key=itemgetter('score'), reverse=True)
    
    response = {
        'cars': recommendations
    }
    print(response)
    return {
        'statusCode': 200,        
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(response)
    }
