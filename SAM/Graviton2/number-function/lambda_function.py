import json
import urllib.request
import numpy as np

def lambda_handler(event, context):
    body = event['body']
    res = urllib.request.urlopen('http://numbersapi.com/'+ str(body['number']) + '/' + body['type'])
    responsebody = res.read().decode('utf-8')

    response = {
        'isBase64Encoded': False,
        'headers': {
            'Content-Type': 'application/json',
        },
        'statusCode': 200,
        'body': json.dumps(responsebody)
    }
    return response