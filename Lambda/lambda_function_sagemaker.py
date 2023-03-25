import os
import io
import boto3
import json
import csv
import logging

# It is good practice to use proper logging.
# Here we are using the logging module of python.
# https://docs.python.org/3/library/logging.html

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# grab environment variables
ENDPOINT_NAME = os.environ['ENDPOINT_NAME']



def lambda_handler(event, context):
  
   # Using sagemaker boto3 client.
   # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sagemaker.html

   # Test Data of 3 movie reviews
   client = boto3.client('sagemaker-runtime')
   test_file = io.StringIO('["The movie was horrible","This should be awarded an Oscar","I did not like the ending"]')
   payload = test_file.getvalue()              
    
   # Make sure to edit the Lambda's function Environment variable and Set ENDPOINT_NAME to a valid value from sagemaker
   response = client.invoke_endpoint(
     EndpointName=ENDPOINT_NAME,
     ContentType='text/csv',
     Body=payload,
     Accept='Accept'
     )
  
   # Expected output should be 1 for a positive review or 0 for a negative.
   prediction = response['Body'].read().decode('utf-8')
   return prediction
