"""
This lambda function Generates fake data and uploads to the bucket.
"""

import json
import sys
import os
import boto3
from botocore.exceptions import ClientError
import logging
import urllib3
http = urllib3.PoolManager()
SUCCESS = "SUCCESS"
FAILED = "FAILED"

import random
import datetime
from faker import Faker
from faker.providers import bank, credit_card, date_time, profile,currency, user_agent, job
from faker_vehicle import VehicleProvider

# It is a good practice to use proper logging.
# Here we are using the logging module of python.
# https://docs.python.org/3/library/logging.html

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')
bucket_name = os.environ['BUCKET_NAME']
filename_list = []
responseData = {'status': 'NONE'}


def lambda_handler(event, context):
    logger.info(f'event: {event}')
    try:
        if event['RequestType'] == 'Create' or event['RequestType'] == 'Update':
            try:
                generate_data(100)
                logger.info(f"Upload Complete")
                responseData['status'] = 'Upload Complete'
                send(event, context, SUCCESS, responseData ,physicalResourceId=event['LogicalResourceId'])
            except Exception as e:
                logger.info(f"Error: {e}")
                responseData['status'] = f'FAILED TO COPY. ERROR {e}'
                send(event, context, SUCCESS, responseData ,physicalResourceId=event['LogicalResourceId'])
        elif event['RequestType'] == 'Delete':
            responseData['status'] = f'DELETE IN PROGRESS'
            send(event, context, SUCCESS, responseData ,physicalResourceId=event['LogicalResourceId'])
    except Exception as e:
        logger.info(f"Error: {e}")
        try:
            generate_data(100)
            logger.info(f"Upload Complete")
        except Exception as e:
            logger.info(f"Error: {e}")
    


def generate_data(num_records):
    logger.info("Generating data")
    # Call the get_secrets() function to get data from Secrets manager
    faker = Faker()

    # list of fake toll plaza name
    toll_plaza_list = ["buckley_rd","82nd_st","royal_ave","savanna_west","golf_rd","york_rd"]
    # toll_booth_name = random.choice(toll_plaza_list)
    

    fake = Faker()
    fake.add_provider(bank)
    fake.add_provider(credit_card)
    fake.add_provider(profile)
    fake.add_provider(date_time)
    fake.add_provider(currency)
    fake.add_provider(user_agent)
    fake.add_provider(job)
    fake.add_provider(VehicleProvider)


    fake_data = {}
    for n in range(0,num_records):
        date_obj = datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 30))
        transaction_date = date_obj.strftime("%Y/%m/%d")
        toll_price = faker.random_int(1, 1000) / 100.0
        toll_plaza_name = random.choice(toll_plaza_list)
        fake_data["transaction_id"] = fake.random_number(5)
        fake_data["transaction_date"] = transaction_date
        fake_data["toll_booth"] = toll_plaza_name
        fake_data["vehicle_make"] = fake.vehicle_make()
        fake_data["vehicle_category"] = fake.vehicle_category()
        fake_data["transaction_amount"] = toll_price

        with open('/tmp/sample_data.json', 'a') as f_object:
            f_object.write(f"{fake_data}\n")
 
    print("File has been created.")

    try:
        response = s3.upload_file(
            '/tmp/sample_data.json',
            Bucket=bucket_name,
            Key=f'sample_data-{datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")}.json'
            )
        logger.info('File Uploaded Successfully')
    except ClientError as e:
        logging.error(e)
        logger.info('File Not Uploaded')
    else:
        logger.info('empty list')

def send(event, context, responseStatus, responseData, physicalResourceId=None, noEcho=False, error=None):
    responseUrl = event['ResponseURL']

    logger.info(responseUrl)

    responseBody = {}
    responseBody['Status'] = responseStatus
    if error is None: 
        responseBody['Reason'] = 'See the details in CloudWatch Log Stream: ' + context.log_stream_name + ' LogGroup: ' + context.log_group_name
    else:
        responseBody['Reason'] = error
    responseBody['PhysicalResourceId'] = physicalResourceId or context.log_stream_name
    responseBody['StackId'] = event['StackId']
    responseBody['RequestId'] = event['RequestId']
    responseBody['LogicalResourceId'] = event['LogicalResourceId']
    responseBody['NoEcho'] = noEcho
    responseBody['Data'] = responseData

    json_responseBody = json.dumps(responseBody)

    print("Response body:\n" + json_responseBody)

    headers = {
        'content-type' : '',
        'content-length' : str(len(json_responseBody))
    }
    try:
        response = http.request('PUT',responseUrl,body=json_responseBody.encode('utf-8'),headers=headers)
        print("Status code: " + response.reason)
    except Exception as e:
        print("send(..) failed executing requests.put(..): " + str(e))