import json
import sys
import os
import boto3
import logging
import requests
import base64
import tarfile
import time

from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Get the environment vairable values.
bank_api_url = os.environ["bank_api_URL"]
sign_kms_id = os.environ["sign_KMS_ID"]

api_client = boto3.client('apigateway')
kms_client = boto3.client('kms')

firehose_client = boto3.client('firehose')
timestamp = time.time()
bank_response = "502"
data={}


def lambda_handler(event, context):
    # Record the events.
    logger.info("Received event in frontend customer API Gateway.")
    logger.info(json.dumps(event))

    # Use AWS KMS to sign the message body.
    raw_data = event['body']
    response = kms_client.sign(
            KeyId=sign_kms_id,
            Message=raw_data,
            MessageType='RAW',
            SigningAlgorithm='RSASSA_PKCS1_V1_5_SHA_256')
    logger.info('Sigature generated for the message body.')
    logger.info(response['Signature'])
    
    ## Encode the signature to base64. 
    sigB64 = base64.urlsafe_b64encode(response['Signature'])
    encoded_signature = sigB64.decode("utf-8")
    logger.info('Encoded_signature.')
    logger.info(encoded_signature)   

    signedJWT = f'{raw_data}.{encoded_signature}'
    headers = {'Content-Type': 'application/json'}
    data = {"jwtData": signedJWT}
    logger.info('Data with encoded signature.')
    logger.info(data)

    # Send a POST command with the signed messages to the bank API Gateway.
    # Signature is verified in the bank.
    post_response = requests.post(bank_api_url, headers=headers,data = data)

    verified = False

    if post_response.status_code == 200:
        # Signature is verified when status code is 200.
        verified = True
        # Send logs to Amazon Kinesis Data Firehose.
        send_logs(post_response,verified,timestamp,data)
        logger.info("Success! Verify signature passed.")
        return {
            'statusCode': 200,
            'body': json.dumps('Hello from signing Lambda function! Verified signature - Success!')
        } 
    else:
        send_logs(post_response,verified,timestamp,data)
        logger.info("Failed! Verify signature failed.")
        return {
            'statusCode': post_response.status_code,
            'body': json.dumps('Hello from signing Lambda function! Cannot verify signature - Failed!')
        }

def send_logs(bank_response, verified, timestamp, my_data):
    ### This function sends logs to Amazon Kinesis Data Firehose.   
    # Build the logs information.
    json_log = {
        'status_code' : bank_response.status_code,
        'response': bank_response.json(),
        'verified': verified,
        'data':my_data,
        'event_timestamp': int(timestamp)
    }

    # Call put_record to send logs to Kinesis Data Firehose.    
    firehose_response = firehose_client.put_record(
            DeliveryStreamName = "secure-payment-logs-stream",
            Record ={
                'Data': json.dumps(json_log)
            }
        )    
    
    logger.info("Sent logs to Amazon Kinesis Data Firehose and stored logs in an Amazon S3 logs bucket.")
    logger.info(json_log) 
    logger.info("Received Kinesis Data Firehose response.")   
    logger.info(firehose_response)
    