import json
import boto3
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
athena = boto3.client('athena')

bucket_name = os.environ['STREAM_BUCKET_NAME']
result_output_location = "s3://" + bucket_name + "/athena/results/"
database_name = 'clickstream'

def lambda_handler(event, context):
    json_event = json.dumps(event)
    print("[INFO] event: " + json_event)
    logger.info("Create a database")
    create_database()
    logger.info("Create Athena Table")
    create_table()

############################################################################################################
## Create athena database
def create_database():
    
    response = athena.start_query_execution(
        QueryString='create database ' + database_name,
        ResultConfiguration={
            "OutputLocation": result_output_location
        },
        WorkGroup='clickstream'
    )
    

############################################################################################################
## Create athena table
def create_table():
    
    ddl_text = f"""CREATE EXTERNAL TABLE {database_name}.my_ingested_data (
EVENT_TIME DATE,
TICKER_SYMBOL STRING,
CHANGE DOUBLE,
SECTOR STRING,
PRICE DOUBLE
)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
with serdeproperties ( 'paths'='TICKER_SYMBOL, SECTOR, PRICE, CHANGE, EVENT_TIME' )
LOCATION "s3://{bucket_name}/clickstream/"
"""
    
    response = athena.start_query_execution(
        QueryString=ddl_text,
        ResultConfiguration={
            "OutputLocation": result_output_location
        },
        WorkGroup='clickstream'
    )
    