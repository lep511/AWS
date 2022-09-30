"""
This lambda function loads data to the mysql test server.
The Lambda function also gets custom queries against the database.
The results is then saved to the S3 Bucket.
"""

import json
import sys
import pymysql
import os
import csv
import os
import boto3
import base64
from botocore.exceptions import ClientError
import logging
import db

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
    
    # Call the get_secrets() function to get data from Secrets manager
    result = get_secret()
    result = json.loads(result)
    
    # Retreive RDS details from the Secrets manager response
    host = result.get('host')
    port = result.get('port')
    username = result.get('username')
    password = result.get('password')
    db_name = result.get('dbname')
    
    logger.info(f"host = {host}")
    logger.info(f"username = {username}")
    logger.info(f"password = {password}") 
    logger.info(f"db_name={db_name}") 
    
###### START: Uncomment below section to test RDS connection ######
    
    # try:
    #     conn = pymysql.connect(host=host, user=username, passwd=password, db=db_name, connect_timeout=5)
    #     cursor = conn.cursor()
    # except pymysql.MySQLError as e:
    #     logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
    #     logger.error(e)
    #     sys.exit()
    
    # logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")
    
    # cursor.execute("SHOW TABLES LIKE 'talentpool'")
    # result = cursor.fetchone()
    
    # if not result:
    #     load_data()
    # else:
    #     custom_query(host,username,password,db_name,port)

###### END: Uncomment section to test RDS connection ######

def custom_query(host,username,password,db_name,port):
    
    custom_sql = """
        SELECT * FROM talentpool
        WHERE occupation LIKE 'Toxicologist';
        """
    
    custom_query = database.query(custom_sql,host,username,password,db_name,port)
    logger.info(custom_query)
    
    with open('/tmp/results.json', 'w') as f:
        f.write(json.dumps(custom_query))
    filename = '/tmp/results.json'

    # Boto3 - s3 Client
    # You will use the client to upload files to S3 bucket
    # More Info: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.put_object
    
###### START: Uncomment below section to test S3 connection ######

    # s3 = boto3.client('s3')
    
    # try:
    #     response = s3.upload_file(
    #         filename,
    #         Bucket='Enter_your_bucket_name',
    #         Key='results.json'
    #         )
    #     logger.info('File Uploaded Successfully')
    # except ClientError as e:
    #     logging.error(e)
    #     logger.info('File Not Uploaded')
        
###### End: Uncomment above section to test S3 connection ######    
    
def load_data():
    """
    This code loads the data in the database server using the data.csv file.
    The data.csv file contains the sample data generated using Faker.
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
    
    # Read the data.csv file
    with open('data.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        talentpool = list(reader)
    
    # Define the SQL statement to create table
    talentpool_sql = """
        create table talentpool (
        first_name nvarchar(200),
        last_name nvarchar(200),
        occupation nvarchar(200),
        company nvarchar(200),
        dob nvarchar(200),
        country nvarchar(200)
        );
        """
    
    # Initiate connection to database    
    conn = pymysql.connect(host=host, user=username, passwd=password, db=db_name, connect_timeout=5)
    cursor = conn.cursor()

    logger.info("Creating talentpool table")
    conn.cursor().execute(talentpool_sql)
    conn.commit()
    logger.info('done')

    logger.info("Populating talentpool table")
    for item in talentpool:
        sql = """INSERT INTO `talentpool` (first_name,last_name,occupation,company,dob,country) VALUES (%s,%s,%s,%s,%s,%s);"""
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (item["first_name"], item["last_name"], item["occupation"], item['company'], item['dob'],
                                  item["country"]))
                conn.commit()
        except:
            logger.info(("Unexpected error! ", sys.exc_info()))
            sys.exit("Error!")
    
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