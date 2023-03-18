"""
This lambda function loads data to the mysql test server.
The Lambda function also gets custom queries against the database.
The results is then saved to the S3 Bucket.
"""

import json
import sys
import pymysql
import os
import boto3
from botocore.exceptions import ClientError
import logging
import db
import urllib3
http = urllib3.PoolManager()
SUCCESS = "SUCCESS"
FAILED = "FAILED"

import random
import datetime
from faker import Faker

# It is a good practice to use proper logging.
# Here we are using the logging module of python.
# https://docs.python.org/3/library/logging.html

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize class DB
database = db.DB()

# Declare the secrets manager arn and region
secret_name = os.environ['secret_arn']
region_name = "us-east-1"

def lambda_handler(event, context):
    logger.info(f'event: {event}')
    
    # Call the get_secrets() function to get data from Secrets manager
    result = get_secret()
    result = json.loads(result)
    
    # Retreive RDS details from the Secrets manager response
    host = result.get('host')
    port = result.get('port')
    username = result.get('username')
    password = result.get('password')
    db_name = result.get('dbname')
    
    logger.info(f"host = {host}, port = {port}, username = {username}, password = {password}, db_name={db_name}")
    
###### START: Test RDS connection and load data ######
    conn = pymysql.connect(host=host, user=username, passwd=password, db=db_name, connect_timeout=5)
    cursor = conn.cursor()
    try:
        logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")
        cursor.execute("SHOW TABLES LIKE 'customers'")
        result = cursor.fetchone()

        if event['RequestType'] == 'Create':
            if not result:
                create_tables()
                load_data('customers', 100)
                load_data('transactions', 2000)
            else:
                custom_query(host,username,password,db_name,port)
        send(event, context, SUCCESS, {},physicalResourceId=event['LogicalResourceId'])
    except Exception as e:
        logger.info(f"exception: {e}")
        send(event, context, SUCCESS,{}, physicalResourceId='12345678')

    conn.close()
###### END: RDS connection complete ######

def custom_query(host,username,password,db_name,port):
    
    custom_sql = """
        SELECT customers.first_name FROM customers;
        """
    
    custom_query = database.query(custom_sql,host,username,password,db_name,port)
    logger.info(custom_query)


def create_tables():
    """
    This code creates tables
    """
    # Call the get_secrets() function to get data from Secrets manager
    result = get_secret()
    result = json.loads(result)
    
    # Retreive RDS details from the Secrets manager response
    host = result.get('host')
    port = result.get('port')
    username = result.get('username')
    password = result.get('password')
    db_name = result.get('dbname')

    # Define the SQL statement to create table
    customers_sql = """
        create table if not exists customers (
        customer_id int primary key auto_increment,
        first_name nvarchar(200),
        last_name nvarchar(200),
        email nvarchar(200),
        address nvarchar(200),
        dob date not null
        );
        """
    transactions_sql = """
        create table if not exists transactions (
        transaction_id int primary key auto_increment,
        transaction_date date not null,
        customer_id int,
        product_name nvarchar(200),
        product_price numeric(10,2),
        foreign key(customer_id) references customers(customer_id)
        );
        """

    # Initiate connection to database
    conn = pymysql.connect(host=host, user=username, passwd=password, db=db_name, connect_timeout=5)
    cursor = conn.cursor()

    logger.info("Creating talentpool table")
    conn.cursor().execute(customers_sql)
    conn.cursor().execute(transactions_sql)
    conn.commit()
    logger.info('done')
    conn.close()


def load_data(table_name, num_records):
    logger.info("Populating data")
    # Call the get_secrets() function to get data from Secrets manager
    result = get_secret()
    result = json.loads(result)
    
    # Retreive RDS details from the Secrets manager response
    host = result.get('host')
    port = result.get('port')
    username = result.get('username')
    password = result.get('password')
    db_name = result.get('dbname')
    
    faker = Faker()

    # list of fake products to insert into the products table
    product_list = ["hat", "cap", "shirt", "sweater", "sweatshirt",
                    "shorts", "jeans", "sneakers", "boots", "coat", "accessories"]
    # Initiate connection to database
    conn = pymysql.connect(host=host, user=username, passwd=password, db=db_name, connect_timeout=5)
    cursor = conn.cursor()

    if table_name == "customers":
        for _ in range(num_records):
            first_name = faker.first_name(),
            last_name = faker.last_name(),
            email = faker.email(),
            address = faker.address(),
            dob = faker.date_of_birth(minimum_age=16, maximum_age=60)
            sql = """INSERT INTO `customers` (first_name,last_name,email,address,dob) VALUES (%s,%s,%s,%s,%s);"""

            try:
                with conn.cursor() as cur:
                    cur.execute(sql, (first_name, last_name, email, address, dob))
                    conn.commit()
            except:
                logger.info(("Unexpected error! ", sys.exc_info()))
                sys.exit("Error!")

    if table_name == "transactions":
        for _ in range(num_records):
            product_name = random.choice(product_list),
            product_price = faker.random_int(1, 100000) / 100.0
            date_obj = datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 30))
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                cust_sql = """select customers.customer_id from customers;"""
                cur.execute(cust_sql)
                cust = cur.fetchall()

            transaction_date = date_obj.strftime("%Y/%m/%d")
            customer_id = random.choice(cust).get('customer_id')

            sql = """INSERT INTO `transactions` (transaction_date,customer_id,product_name,product_price) VALUES (%s,%s,%s,%s);"""

            try:
                with conn.cursor() as cur:
                    cur.execute(sql, (transaction_date, customer_id, product_name, product_price))
                    conn.commit()
            except:
                logger.info(("Unexpected error! ", sys.exc_info()))
            #     sys.exit("Error!")
    conn.close()

def get_secret():
    """
    This code retreives RDS details from the secrets manager.
    """
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    
    # Getting the secrets from secrets manager
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
        return get_secret_value_response.get('SecretString')
    except ClientError as e:
        print(e)

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
