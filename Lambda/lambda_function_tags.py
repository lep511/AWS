"""
This lambda function reviews tags in all the instance and 
Updates the required tags
"""

import json
import sys
import os
import os
import boto3
import base64
from botocore.exceptions import ClientError
import logging

# It is a good practice to use proper logging.
# Here we are using the logging module of python.
# https://docs.python.org/3/library/logging.html

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(event)
    
    client = boto3.client('sts')
    response_account = client.get_caller_identity()['Account']
    
    instance = event
    resourse_ARN = f"arn:aws:ec2:us-east-1:{response_account}:instance/{instance}"
    logger.info(resourse_ARN)
    
    
    tag_client = boto3.client('resourcegroupstaggingapi')
    try:
        response_tag = tag_client.tag_resources(
                 ResourceARNList=[
                     resourse_ARN,
                 ],
                 Tags={
                    'Environment':'Prod'
                 }
                     )
        print(response_tag)
    except Exception as exp:
        logger.exception(exp)
        
    return {
        "compliance_type": "COMPLIANT",
        "annotation": "This resource is compliant with the rule."
    }