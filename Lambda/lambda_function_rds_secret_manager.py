import sys
import logging
import pymysql
import json
import os
import boto3
from botocore.exceptions import ClientError
from botocore.vendored import requests

# rds settings
rds_host = os.environ['RDS_HOST']
name = os.environ['RDS_USERNAME']
secret_name = os.environ['SECRET_NAME']
db_name = os.environ['RDS_DB_NAME']
table_name = os.environ['RDS_Table_NAME']

my_session = boto3.session.Session()
region_name = my_session.region_name
conn = None

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def openConnection():
    global conn
    password = "None"
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager',region_name=region_name)

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        print(get_secret_value_response)
    except ClientError as e:
        print(e)
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            j = json.loads(secret)
            password = j['password']
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            print("password binary:" + decoded_binary_secret)
            password = decoded_binary_secret.password

    try:
        #print("Opening Connection")
        if(conn is None):
            conn = pymysql.connect(host=rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
        elif (not conn.open):
            # print(conn.open)
            conn = pymysql.connect(host=rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
    except Exception as e:
        print (e)
        print("ERROR: Unexpected error: Could not connect to MySql instance.")
        raise e

def lambda_handler(event, context):
    try:
        # Query sample data in RDS instance
        openConnection()
        #get id from API Gateway

        sql = 'select Name from ' + table_name + ' where id=' + event["id"]
        response = []

        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
            # list comprehensions
            playerNames = [row[0] for row in rows]

            for playerName in playerNames:
                result = "My favorite player is " + playerName
                response.append(result)

        return response
    except Exception as e:
        # Error while opening connection or processing
        print(e)
        err_msg = "Please make sure you provided query string like URL/?id=1"
        return err_msg