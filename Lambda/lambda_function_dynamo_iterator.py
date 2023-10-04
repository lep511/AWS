import json
import boto3
import os
import sys 

dynamo = boto3.client("dynamodb")
table_name = os.environ['DDB_TABLE_NAME']
paginator = dynamo.get_paginator('scan')

def lambda_handler(event, context):

    response_iterator = paginator.paginate(
        TableName=table_name,
        Select='ALL_ATTRIBUTES'
       
        )
    all_predictions = []
    for response in response_iterator:
        all_predictions = all_predictions + response['Items']

    response = {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,GET'
        },
        'body': json.dumps({'data': all_predictions})
    }
    
    return response