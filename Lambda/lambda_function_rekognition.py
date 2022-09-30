"""
The code is developed using reference from
https://docs.aws.amazon.com/rekognition/latest/customlabels-dg/ex-lambda.html

"""

import json
import logging
import boto3

# It is good practice to use proper logging.
# Here we are using the logging module of python.
# https://docs.python.org/3/library/logging.html

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Declare the label that is used to identify
# if the image contains the label

LABEL = '<Add_Your_Label>'

# Using boto3 S3 Client
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#client
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """
    This code gets the S3 attributes from the trigger event,
    then invokes the rekognition api to detect labels.
    If the label matches the one present on the LABELS list,
    response is written in the S3 bucket with "Status":"Label Found",
    else the response is written in the S3 bucket with "Status":"Label Not Found".
    """
    logger.info(event)
    bucket = event['Records'][0]['s3']['bucket']['name']
    image = event['Records'][0]['s3']['object']['key']
    output_key = 'output/rekognition_response.json'
    response = {'Status': 'Not Found', 'body': []}


    # Using rekognition boto3 client.
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rekognition.html

    rekognition_client = boto3.client('rekognition')

    # Identify label
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rekognition.html#Rekognition.Client.detect_labels

    try:
        response_rekognition = rekognition_client.detect_labels(   # You are calling detect_labels API 
            Image={                                                # to analyzing Images Stored in an Amazon S3 Bucket
                'S3Object': {
                    'Bucket': bucket,
                    'Name': image
                }
            },
            MinConfidence=70                                        # MinConfidence specifies the minimum confidence  
        )                                                           # level for the labels to return.

    
    # The below code section tries to find all labels in the detect_labels 
    # list. If the label is found in the list, the response JSON file is updated with 
    # "Status":"Success! <label_name> found" then updates the response body with all 
    # detected labels. If the label is not found, the response JSON file is updated with 
    # "Status":"Failed, <label_name> not found" then updates the response body with all 
    # detected labels.
        
        detected_labels = [] # Declaring empty label lists.
        
        if response_rekognition['Labels']:
            for label in response_rekognition['Labels']:
                detected_labels.append(label['Name'].lower())
            print(detected_labels)
        
            if LABEL in detected_labels:
                response['Status'] = f"Success! {LABEL} found"
                response['body'].append(response_rekognition['Labels'])
            else:
                response['Status'] = f"Failed! {LABEL} Not found"
                response['body'].append(response_rekognition['Labels'])
                
    except Exception as error:
        print(error)

# Finally the file will be written in the S3 bucket output folder.
    s3_client.put_object(
      Bucket=bucket,
      Key=output_key,
      Body=json.dumps(response, indent=4)
    )

    return response

'''
You can use below code to create test event to test
the Lambda function.
{
    "Records": [
                {
                "s3": {
                    "bucket": {
                    "name": "<Your_bucket_name>"
                    },
                    "object": {
                    "key": "input/ovni.png"
                    }
                }
                }
            ]
}
'''

# You can visit https://docs.aws.amazon.com/code-samples/latest/catalog/code-catalog-python-example_code-rekognition.html
# to get more sample codes.