# This Lambda function displays informational messages about the state of the application.
# Please review the comments for each code block to help you understand the execution of this Lambda function.

import os
import json
import boto3
import logging
from datetime import datetime
from botocore.exceptions import ClientError

# AWS Lambda Function Logging in Python - More info: https://docs.aws.amazon.com/lambda/latest/dg/python-logging.html
logger = logging.getLogger()
logger.setLevel(logging.INFO)


session = boto3.Session()
# Boto3 - DynamoDB Client - Mode Info: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html
dynamodb = session.resource("dynamodb")

# You can use SAM (template.yaml) to automatically create a table in DynamoDB 
# (AWS :: Serverless :: SimpleTable), to choose the name remember to use the TableName parameter
# https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-resource-simpletable.html
# Table name to fetch a message
table_name = 'app_table'

app_table = dynamodb.Table(table_name)

# The Lambda handler is the first function that executes in your code.
def lambda_handler(event, context):

    # context – AWS Lambda uses this parameter to provide runtime information to your handler.
    # event – AWS Lambda uses this parameter to pass in event data to the handler. This parameter is usually of the Python dict type.
    # AWS Lambda function Python handler - https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html
    
    # Event received from API Gateway Lambda Proxy Integration
    #
    #   In Lambda proxy integration, when a client submits an API request, API Gateway passes 
    # to the integrated Lambda function the raw request as-is in event parameter
    # Input Format https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    print('Received event: ' + json.dumps(event, indent=2))
    
    # variable with informational message - This message will be printed if there is no Query String
    msg = 'Template message created' 

    # On the World Wide Web, a query string is a part of a uniform resource locator (URL) that assigns values to specified parameters.
    # https://en.wikipedia.org/wiki/Query_string    
    queryStringParameters = event.get('queryStringParameters')
    if queryStringParameters is not None:
        # Found the QueryStringParameter, searching for the id key, for example, Query String => id=1
        id = queryStringParameters.get('id')
        if id is not None:
            # Found the id, usually you use the query string parameter to filter, paginate 
            # or search the database for information, in this lab we will only display a message.
            
            # Uncomment the two lines below if you configured DynamoDB in the SAM template
            # str_id = str(id) # convert id to string to match with DynamoDB partition key type
            # msg = 'Template with message {}'.format(get_item(str_id))  
            
            # Comment the line below if you going to use DynamoDB
            msg = 'Template with message id = {}'.format(id)
    
    
    #   In Lambda proxy integration, API Gateway requires the backend Lambda function to return output
    # to API Gateway, then API Gateway sends the return to the client
    # Output format: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-output-format
    response = {
        'statusCode': '200',
        'body': msg,
        'headers': {
            'Content-Type': 'application/json',
        }
    }
    
    return response
    
    
# Use this function to search for a message in DynamoDB, note that this function will only find the table if
# It was created in SAM (template.yaml) with the name declared at the beginning of this function (variable table_name)
def get_item(id):
    try:
        ret = app_table.get_item(
            Key={ 'id': id }
        )
        logger.info({"operation": "query a item", "details": ret})

        if 'Item' not in ret:
            print("I found the table but there is no item in it with this id, you can create an item in DynamoDB using the console.")

        # Return the Item - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.get_item
        return ret['Item']
    except ClientError as err:
        logger.debug({"operation": "query a item", "details": err})
        if err.response['Error']['Code'] == 'ResourceNotFoundException':
            print("I didn't find the table, did you create the resource in the template.yaml (SAM template) and remember to deploy it?")
        return err