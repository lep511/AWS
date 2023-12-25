"""
This lambda function invokes SageMaker endpoint
and reads the response. This application also 
updates the DynamoDB table.
"""
import json, os
import boto3
from datetime import datetime
import random
import logging
import uuid
import random

# It is a good practice to use proper logging.
# Here we are using the logging module of python.
# https://docs.python.org/3/library/logging.html

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(json.dumps(event))

    # Extract payload from event
    payload = event['payload']

    # Invoke the SageMaker endpoint
    probability = invoke_sagemaker_endpoint(payload)

    ############## DIY ########################
    # 1. Add a DynamoDB table
    # 2. Update DynamoDB table in environment variable
    # 3. Call update_dynamodb_table(event, probability) function
    # 4. Remember to convert probability to string
    ############################################

    return {
        'statusCode': 200,
        'body': {
            'probability': probability
        }
    }

def invoke_sagemaker_endpoint(payload):
    # Get the endpoint name from an environment variable
    endpoint_name = os.environ['ENDPOINT_NAME']

    # Create a SageMaker runtime client
    client = boto3.client('sagemaker-runtime')

    try:
        response = client.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType='text/csv',
            Body=payload
        )
    except Exception as e:
        logger.info(e)

    # Parse the response
    probability = response['Body'].read().decode('utf-8').strip().split(',')

    return probability

def update_dynamodb_table(event, probability):
    # Initialize a DynamoDB client
    dynamodb = boto3.client('dynamodb')

    # Generate a random UUID as the ID
    item_id = str(uuid.uuid4())

    # Get the name of the DynamoDB table from an environment variable
    table_name = os.environ['DYNAMODB_TABLE_NAME']

    # Parse the payload data
    payload = event['payload']
    payload_data = payload.split(',')

    # Save the payload and result in DynamoDB
    item = {
        'id': {'S': item_id}, # Use generated ID as the Item ID
        'encounterclass': {'S': payload_data[0]},
        'gender': {'S': payload_data[1]},
        'marital': {'S': payload_data[2]},
        'ethnicity': {'S': payload_data[3]},
        'race': {'S': payload_data[4]},
        'reasoncode': {'S': payload_data[5]},
        'encounters_code': {'S': payload_data[6]},
        'procedures_code': {'S': payload_data[7]},
        'healthcare_expenses': {'N': payload_data[8]},
        'healthcare_coverage': {'N': payload_data[9]},
        'total_claim_cost': {'N': payload_data[10]},
        'payer_coverage': {'N': payload_data[11]},
        'base_encounter_cost': {'N': payload_data[12]},
        'base_cost': {'N': payload_data[13]},
        'providers_utilization': {'N': payload_data[14]},
        'age': {'N': payload_data[15]},
        'probability': {'S': probability}
    }
    dynamodb.put_item(TableName=table_name, Item=item)
    logger.info("DynamoDB table updated")
