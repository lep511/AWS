import boto3
import json
import os
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

bucket_name = os.environ.get("BUCKET_NAME")
json_file = os.environ.get("JSON_FILE")
table_name = "transactions"
tmp_csv_file = '/tmp/' + json_file 
s3 = boto3.resource('s3')
db_table = boto3.resource('dynamodb').Table(table_name)
    
def fill_table(db_table, table_data):
    try:
        with db_table.batch_writer() as writer:
            for item in table_data:
                writer.put_item(Item=item)
        logger.info("Loaded data into table %s.", db_table.name)
    except ClientError:
        logger.exception("Couldn't load data into table %s.", db_table.name)
        raise

def lambda_handler(event, context):
    result = []
    s3.meta.client.download_file(
                bucket_name, 
                json_file, 
                tmp_csv_file)
    result = json.loads(open(tmp_csv_file, 'r').read())
    fill_table(db_table,result)
        
    return {'statusCode': 200}
