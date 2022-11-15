import json
import boto3
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
athena = boto3.client('athena')

bucket_name = os.environ['STREAM_BUCKET_NAME']
result_output_location = "s3://" + bucket_name + "/athena-results/"
database_name = 'clickstream'

def lambda_handler(event, context):
    json_event = json.dumps(event)
    print("[INFO] event: " + json_event)


############################################################################################################
## Create athena database
def create_database():

    response = athena.start_query_execution(
        QueryString='CREATE DATABASE IF NOT EXISTS ' + database_name,
        ResultConfiguration={
            "OutputLocation": result_output_location
        }
    )
    
    return response['QueryExecutionId']

############################################################################################################
## Create athena table
def create_table():
    
    datehour = 'datehour'
    ddl_text = f"""CREATE EXTERNAL TABLE {database_name}.my_ingested_data (
EVENT_TIME STRING,
TICKER_SYMBOL STRING,
CHANGE DOUBLE,
SECTOR STRING,
PRICE DOUBLE
)
PARTITIONED BY (
datehour STRING
)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
with serdeproperties ( 'paths'='TICKER_SYMBOL, SECTOR, CHANGE, PRICE, EVENT_TIME' )
LOCATION "s3://{bucket_name}/"
TBLPROPERTIES (
"projection.enabled" = "true",
"projection.datehour.type" = "date",
"projection.datehour.format" = "yyyy/MM/dd/HH",
"projection.datehour.range" = "2021/01/01/00,NOW",
"projection.datehour.interval" = "1",
"projection.datehour.interval.unit" = "HOURS",
"storage.location.template" = "s3://{bucket_name}/${{datehour}}/"
)"""
    
    response = athena.start_query_execution(
        QueryString=ddl_text,
        ResultConfiguration={
            "OutputLocation": result_output_location
        }
    )
    