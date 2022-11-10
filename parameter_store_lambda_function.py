import json
import os
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

print('Loading function')

#Updates an SSM parameter
#Expects parameterName, parameterValue
def lambda_handler(event, context):
    json_event = json.dumps(event)
    print("--event: " + json_event)

    # get SSM client
    client = boto3.client('ssm')
    parameterName = event['detail']['name']
    
    # Get the parameter store value
    response = client.get_parameter(
        Name=parameterName,
        WithDecryption=False
    )
    print(response)
    return {"Data" : response["Parameter"]["Value"]}

"""
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "ssm:PutParameter",
            "Resource": "arn:aws:ssm:us-east-2:855918939771:parameter/s3-bucket-for-app"
        },
        {
            "Effect": "Allow",
            "Action": "ssm:GetParameter",
            "Resource": "arn:aws:ssm:us-east-2:855918939771:parameter/s3-bucket-for-app"
        },
        {
            "Effect": "Allow",
            "Action": "ssm:DescribeParameters",
            "Resource": "*"
        }
    ]
}
"""