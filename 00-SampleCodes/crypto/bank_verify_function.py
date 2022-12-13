import json
import sys
import os
import boto3
import logging
import base64
import urllib.parse
import re

from OpenSSL.crypto import load_publickey, FILETYPE_PEM, verify, X509

from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info("Received event from the bank API Gateway.")
    logger.info(json.dumps(event))
    
    response  = {
    'statusCode': 200,
    'headers': {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Credentials': 'true'
    },
    'body': ''
    }
    
    raw_data = event['body']
    raw_data = raw_data.replace('jwtData=', '')
    logger.info("Extracted the message body from the event.")
    logger.info(raw_data)
    
    # urllib.parse module defines a standard interface to break Uniform Resource Locator (URL) strings up into components, 
    # to combine the components back into a URL string, and to convert a “relative URL” to an absolute URL given a “base URL.
    decoded_messages = urllib.parse.unquote_plus(raw_data)
    logger.info("Decoded the message body.")
    logger.info(decoded_messages)
    
    split_data = re.split(r"(>)\.",decoded_messages)
    logger.info(split_data)
    message = split_data[0]+split_data[1]
    key = split_data[2]
    logger.info("Splitted the request message and the key.")
    logger.info(message)
    logger.info(key)
    
    # Save key and message to a file.
    key = key.encode()
    key = base64.urlsafe_b64decode(key)
    logger.info("Encoded the key in base64 format.")
    logger.info(key)
    
    with open('/tmp/signature.sig', 'wb') as f:
        f.write(key)
    
    with open('/tmp/data.txt', 'w') as f:
        f.write(message)
        
    # Read the signer's public key, received data and signature.

    with open('pubKey.pem') as f:
        public_key_data = f.read()
    
    with open('/tmp/data.txt', 'rb') as f:
        file_data = f.read()
    
    with open('/tmp/signature.sig', 'rb') as f:
        signature = f.read()
        
    # Load the public key
    pkey = load_publickey(FILETYPE_PEM, public_key_data)
    
    # The verify()function expects that the public key is
    # wrapped in an X.509 certificate
    x509 = X509()
    x509.set_pubkey(pkey)
    
    # Verify the signature
    try:
        logger.info('Hello from bank_verify Lambda function, verifying signature.')
        verify(x509, signature, file_data, 'sha256')
        logger.info('Verify signature - Passed.')
        return {
        'statusCode': 200,
        'body': json.dumps('Success! Signature is verified!')
        }
    except:
        logger.info('Verify signature - Failed.')
        return {
        'statusCode': 502,
        'body': json.dumps('Failed! Signature cannot be verified!')
        }
    
