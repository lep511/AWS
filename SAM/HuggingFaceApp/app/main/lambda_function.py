# API_URL = https://api-inference.huggingface.co/models/facebook/bart-large-mnli
# SECRET_NAME = huggingface/apikey

import json
import requests
import boto3
from botocore.exceptions import ClientError
import os

region_name = "us-east-1"


def lambda_handler(event, context):
    print(event)
    output = query({
        "inputs": "Hi, I recently bought a device from your company but it is not working as advertised and I would like to get reimbursed!",
        "parameters": {"candidate_labels": ["refund", "legal", "faq"]},
    })
    print(output)
    return {
        'statusCode': 200,
        'sequence': json.dumps(output['sequence']),
        'labels': json.dumps(output['labels']),
        'scores': output['scores']
    }


def query(payload):
    secret = get_secret()
    secret = json.loads(secret)
    KEY_API = secret['value']
    print(KEY_API)
    headers = {"Authorization": "Bearer " + KEY_API}
    API_URL = os.environ['API_URL']
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()
	
	
def get_secret():
    # Create a Secrets Manager client
    secret_name = os.environ['SECRET_NAME']
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    # Decrypts secret using the associated KMS key.
    return get_secret_value_response['SecretString']
    
