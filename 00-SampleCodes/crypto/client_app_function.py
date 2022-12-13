import json
import sys
import os
import boto3
import logging
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # Record the events
    customer_api = os.environ["frontend_customer_api_url"]

    # Send a XML request for a debit payment
    xml_body = "<?xml version=\"1.0\"?>\n<info>\n<customer id=\"101\">\n<name>Doe,John</name>\n<amount>38.95</amount>\n<type>debit</type>\n</customer>\n</info>"
    
    headers = {"Content-Type": "application/xml"}

    data_payload = xml_body

    logger.info("Message body of the XML request.")
    logger.info(data_payload)

    # Send a post message to the customer frontend API
    r = requests.post(customer_api, headers=headers, data=data_payload)
    
    # Check the status code of the post response to determine if the request was sent successfully.
    logger.info(r.text)
    if r.status_code == 200:
        return {
            'statusCode': 200,
            'body': json.dumps('Success! Sent bank payment request successfully.')
        }
    else:
        return {
            'statusCode': r.status_code,
            'body': json.dumps('Failed! Cannot send bank payment request.')
        }