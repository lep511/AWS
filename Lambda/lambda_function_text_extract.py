"""
This lambda funtion gets triggered from S3 upload.
The document is sent to Amazon Textract for analysis
The form data is then written to the dynamodb forms table.
"""

import json
import logging
import boto3
import uuid



# Python trp module is Amazon textract result parser
# https://pypi.org/project/textract-trp/
# You have uploaded module using Lambda Layer.
from trp import Document
from urllib.parse import unquote_plus

# It is good practice to use proper logging.
# Here we are using the logging module of python.
# https://docs.python.org/3/library/logging.html

logger = logging.getLogger()
logger.setLevel(logging.INFO)

table_name = 'forms'

# Boto3 - s3 Client
# More Info: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rekognition.html
s3 = boto3.client('s3')
dynamodb = boto3.resource( 'dynamodb', region_name='us-east-1' )
dynamodb_client = boto3.client('dynamodb')

# Declare output file path and name
output_key = "output/textract_response.json"
# Generate a unique UUID based on time.
idx = str(uuid.uuid1())
logger.info(idx)
        


def lambda_handler(event, context):
    """
    This code gets the S3 attributes from the trigger event,
    then invokes the textract api to analyze documents synchronously.
    """

    # log the event
    logger.info(event)
    # Iterate through the event
    for record in event['Records']:
        # Get the bucket name and key for the new file
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        # Using Amazon Textract client
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/textract.html
        textract = boto3.client('textract')
        
        # Analyze document
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/textract.html#Textract.Client.analyze_document
        try:
            response = textract.analyze_document(   # You are calling analyze_document API
                Document={                          # to analyzing document Stored in an Amazon S3 Bucket
                    'S3Object': {
                        'Bucket': bucket,
                        'Name': key
                    }
                },
                FeatureTypes=['FORMS',  # FeatureTypes is a list of the types of analysis to perform.
                              ])                            # Add TABLES to the list to return information about
                                                            # the tables that are detected in the input document.
                                                            # Add FORMS to return detected form data. To perform both
                                                            # types of analysis, add TABLES and FORMS to FeatureTypes .

            doc = Document(response)  # You are parsing the textract response using Document.
            
        except Exception as error:
            return {"Status": "Failed", "Reason": json.dumps(error, default=str)}
            
        # Create table forms if not present and update the table with the attributes from textract 
        
        try:
            response_tables = dynamodb_client.list_tables()
            if table_name not in response_tables.get('TableNames'):
                create_table()
                add_item(doc)
                return_result = {"Status": "Success"}
                return return_result
            else:
                add_item(doc)
                return_result = {"Status": "Success"}
                return return_result
        except Exception as error:
            return {"Status": "Failed", "Reason": json.dumps(error, default=str)}

def add_item(doc):
    db_table_form = dynamodb.Table('forms')
    data = {'id': idx }
    
    for page in doc.pages:
        for field in page.form.fields:
            print("Key: {}, Value: {}".format(field.key, field.value))
            key = field.key
            value = field.value
            data[str(key)] = str(value)
    logger.info(data)        

    # Insert the data in the table.
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.put_item
    db_table_form.put_item(
        Item=data)


def create_table():

    try:
        form_table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'KeyType': 'HASH',
                    'AttributeName': 'id'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 2,
                'WriteCapacityUnits': 2
            }
        )
        # Wait until the table creation complete.
        form_table.meta.client.get_waiter( 'table_exists' ).wait( TableName=table_name )
        print(f"Table {table_name} created!")
    except Exception as e:
        print(f"error: {e}")
        pass
"""
You can use below code to create test event to test
the Lambda function.
{
    "Records": [
                {
                "s3": {
                    "bucket": {
                    "name": "<Your_inputbucket_name>"
                    },
                    "object": {
                    "key": "employment_form.png"
                    }
                }
                }
            ]
}
"""
