"""
This lambda function returns html body.
"""
import os
import json
import logging

# It is a good practice to use proper logging.
# Here we are using the logging module of python.
# https://docs.python.org/3/library/logging.html

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logging.info(event)

    response_body = "<html><title>TestLambda</title></head><h1>You have successfully connected to Amazon API Gateway and invoked the AWS Lambda function.</h1><body></body></html>"
    
    return {
    "statusCode": 200,
    "body": response_body,
    "headers": {
        'Content-Type': 'text/html',
            }
        }