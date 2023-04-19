# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import json
import pymysql
import boto3
import botocore
import cfnresponse
import os
from botocore.exceptions import ClientError



# rds settings
rds_host = os.environ['RDS_HOST']
name = os.environ['RDS_USERNAME']
db_name = os.environ['RDS_DB_NAME']
secretname = os.environ['SECRET_NAME']
SUCCESS = "SUCCESS"
FAILED = "FAILED"
my_session = boto3.session.Session()
region_name = my_session.region_name
conn = None

def openConnection():
    global conn
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secretname
        )
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
            password = decoded_binary_secret.password


    try:
        if(conn is None):
            conn = pymysql.connect(
                host=rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
        elif (not conn.open):
            conn = pymysql.connect(
                host=rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)

    except Exception as e:
        print (e)
        print("ERROR: Unexpected error: Could not connect to MySql instance.")
        raise e



def lambda_handler(event, context):

    # For Delete requests, immediately send a SUCCESS response.

    responseData = {}
    responseStatus = SUCCESS
    if event['RequestType'] == 'Delete':
        cfnresponse.send(event, context, responseStatus, responseData, None)
        return True

    try:
        # insert test data in RDS instance
        openConnection()
        with conn.cursor() as cur:
             # create table
            cur.execute(
                "Create Table  if not exists DemoTable (KeyPK int AUTO_INCREMENT Primary Key, FirstName varchar(50), LastName varchar(50))")
            # insert sample data
            cur.execute(
                "Insert into DemoTable (KeyPK, FirstName, LastName) Values (null, \"Diego\", \"Ramirez\")")
            cur.execute(
                "Insert into DemoTable (KeyPK, FirstName, LastName) Values (null, \"Jane\", \"Doe\")")
            cur.execute(
                "Insert into DemoTable (KeyPK, FirstName, LastName) Values (null, \"Akua\", \"Mansa\")")
            conn.commit()

            print ('Created table with sample data and inserted 3 rows.')

    except Exception as e:
        # Error while opening connection or processing
        print(e)
        responseStatus = FAILED
    finally:
        if(conn is not None and conn.open):
            conn.close()
        # send response back to CFN
        cfnresponse.send(event, context, responseStatus, responseData, None)
    return True