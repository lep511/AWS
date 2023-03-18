# Importing the necessary libraries for the code to run.
import sys, os, logging, json, csv
import boto3, pymysql, psycopg2
import pandas as pd
from botocore.exceptions import ClientError
from psycopg2 import OperationalError
from psycopg2 import sql
import urllib3
http = urllib3.PoolManager()
import fakeData 

# This is setting up the logging and responseData for the function.
SUCCESS = "SUCCESS"
FAILED = "FAILED"
 
logger = logging.getLogger()
logger.setLevel(logging.INFO)
responseData = {'status': 'NONE'}
record_num = 100
 

def lambda_handler(event, context):
    """
    This function is generates data for the databases, creates connections to the
    databases, and inserts the data in databases.
    
    :param event: This is the event that triggered the lambda function
    :param context: This is the context object that Lambda passes to the handler. It contains runtime
    information for the Lambda function that is executing
    :return: a dictionary with a key of "Success" and a value of "Data Loaded in both database"
    """
    logger.info(json.dumps(event))
    
    # This is generating fake data for the database.
    try:
        records = record_num
        headers = [
            "Name",
            "PhoneNumber",
            "Address",
            "EmailAddress",
            "AccountNum",
            "LoanType",
            "LoanAmount",
            "IncomeAmount",
            "LoanApproval",
            "CheckingBalance",
            "SavingsBalance",
            "AccountOpenDate"    
        ]
        fakeData.datagenerate(records, headers)
    except Exception as e:
            logger.info(f"Failed to generate data: {e}")

    # This is creating a connection to the loan database and inserting the loan data into the loan
    # database.
    try:
        bucket = os.environ['sourceBucket']
        key = os.environ['key']
        
        accountData = pd.read_csv("/tmp/account_data.csv", sep=',')
        loanData = accountData.loc[:, accountData.columns.drop(['CheckingBalance', 'SavingsBalance', 'AccountOpenDate'])]
        depositData = accountData.loc[:, accountData.columns.drop(['LoanType', 'LoanAmount', 'IncomeAmount', 'LoanApproval'])]


        loan_creds = json.loads(get_secrets(secret_name = "loan-db/admin", region_name = "us-east-1"))
        loanhostname = loan_creds['host']
        loandbname = loan_creds['dbname']
        loanport = loan_creds['port']
        loanusername = loan_creds['username']
        loanpassword = loan_creds['password']

        deposit_creds = json.loads(get_secrets(secret_name = "deposits-db/admin",region_name = "us-east-1" ))
        deposithostname = deposit_creds['host']
        depositdbname = deposit_creds['dbname']
        depositport = deposit_creds['port']
        depositusername = deposit_creds['username']
        depositpassword = deposit_creds['password']
        
        try:
            loan_conn = pymysql.connect(
                host=loanhostname,
                user=loanusername,
                passwd=loanpassword,
                connect_timeout=5)
            loan_cursor = loan_conn.cursor()
            loan_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {loandbname}")
            loan_cursor.execute(f"use {loandbname}")
            loan_cursor.execute("CREATE TABLE IF NOT EXISTS LoanData (Name varchar(255), PhoneNumber varchar(255), Address varchar(255), EmailAddress varchar(255), AccountNum varchar(255), LoanType varchar(255), LoanAmount varchar(255), IncomeAmount varchar(255), LoanApproval varchar(255), PRIMARY KEY (AccountNum))")

            for i,row in loanData.iterrows():
                acctnum = row[4]
                acctexists = loan_cursor.execute(f"SELECT * FROM LoanData where AccountNum like '%{acctnum}%'")
                if acctexists < 1:
                    sql = "INSERT INTO LoanData VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                    loan_cursor.execute(sql, tuple(row))
                    loan_conn.commit()
            logger.info("done")
        except Exception as e:
            logger.info(f"Failed to create MySQL database with following error: {e}")


        

        # This is creating a connection to the deposit database and inserting the deposit data into the
        # deposit database.
        try:
            deposit_conn = psycopg2.connect(
                host=deposithostname,
                user=depositusername,
                password=depositpassword,
                database=depositdbname,
                port=depositport,
                connect_timeout=5)

            deposit_conn.autocommit = True
            dep_cursor = deposit_conn.cursor()

            try:
                dep_cursor.execute("CREATE TABLE DepositData (Name varchar(255), PhoneNumber varchar(255), Address varchar(255), EmailAddress varchar(255), AccountNum varchar(255), CheckingBalance varchar(255), SavingsBalance varchar(255), AccountOpenDate varchar(255), PRIMARY KEY (AccountNum))")
                logger.info(f"Table DepositData created!")
            except Exception as e:
                logger.info(f"Table DepositData already exists.{e}")
            for label, row in depositData.iterrows():
                acctnum = row[4]
                try:
                    action = "INSERT INTO DepositData (Name, PhoneNumber, Address, EmailAddress, AccountNum, CheckingBalance, SavingsBalance, AccountOpenDate) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
                    dep_cursor.execute(action, tuple(row))
                    deposit_conn.commit()
                except Exception as e:
                    logger.info(f"error:{e}")
                    logger.info("accout already exists")
        except OperationalError as e:
            logger.error("ERROR: Unexpected error: Could not create to PostGreSQL database.")
            logger.error(e)
        logger.info("SUCCESS: Connection to RDS PostGreSQL and DB creation succeeded")

        if "RequestType" in event:
            responseData['status'] = 'Database load done'
            send(event, context, SUCCESS, responseData,physicalResourceId=event['LogicalResourceId'])
        else:
            return {"Status" : "Success! Data Loaded in both databases"}
    except Exception as e:
        logger.info(f"FAILED: {e}")
        if "RequestType" in event:
            responseData['status'] = f"FAILED: {e}"
            send(event, context, SUCCESS, responseData,physicalResourceId=event['LogicalResourceId'])
        else:
            return {"Status" : f"Failed to load data. {e}"}

def get_secrets(secret_name, region_name):
    """
    This function takes in a secret name and region name and returns the secret value.
    
    :param secret_name: The name of the secret you created in AWS Secrets Manager
    :param region_name: The region where the secret is stored
    :return: A string of the secret value
    """
    secret_name = secret_name
    region_name = region_name

    # Create a Secrets Manager client
    session = boto3.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    
    # Get Loan DB Info
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    # Decrypts secret using the associated KMS key.
    DBSecret = get_secret_value_response['SecretString']
    return(DBSecret)




def send(event, context, responseStatus, responseData, physicalResourceId=None, noEcho=False, error=None):
    """
    It takes the response URL from the event, and sends a response back to CloudFormation
    
    :param event: The event that triggered the Lambda function
    :param context: This is the context object that is passed to the Lambda function. It contains
    information about the Lambda function and the execution environment
    :param responseStatus: The status of the response. This value must be SUCCESS, FAILED, or
    IN_PROGRESS
    :param responseData: The data that you want to pass back to CloudFormation
    :param physicalResourceId: The physical ID of the resource. This is the ID that you can use to
    identify the resource in the AWS console
    :param noEcho: If true, the value of the resource's properties will be masked in the CloudFormation
    console, defaults to False (optional)
    :param error: The error message to be displayed in the AWS CloudFormation console
    """
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