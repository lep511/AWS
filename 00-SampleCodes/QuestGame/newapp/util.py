import boto3
from trp import Document
import json
import dynamodb
import random
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def dynamodb_client():
    """
    Function: Initialize S3 client
    :returns: returns client
    """
    client = boto3.client('dynamodb')
    return client


def dynamodb_resource():
    """
    Function: Initialize S3 client
    :returns: returns client
    """
    resource = boto3.resource('dynamodb')
    return resource

def create_table(table_name):
    """
    Creates an Amazon DynamoDB table that can be used to store movie data.
    The table uses the release year of the movie as the partition key and the
    title as the sort key.

    :param table_name: The name of the table to create.
    :return: The newly created table.
    """
    try:
        client = dynamodb_client()
        table = client.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'}  # Partition key
            ],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 10, 'WriteCapacityUnits': 10})
        table.wait_until_exists()
    except Exception as err:
        logger.info(
            "Couldn't create table %s. Here's why: %s: %s", table_name,
            err)
        raise
    else:
        return table



def list_dynamodb_tables():
    """
        Function: list_dynamodb_tables
         Purpose: Get the list of dynamodb tables
        :returns: dynamodb tables in your account
    """
    client = dynamodb_client()
    table_response = client.list_tables()

    # check dynamodb bucket list returned successfully
    if table_response['ResponseMetadata']['HTTPStatusCode'] == 200:
        for table_name in table_response.get('TableNames'):
            print(f" *** Table Name: {dynamodb_client['Name']} - exists \n")
    else:
        print(f" *** Failed while trying to get table list from your account")


def add_items_in_table(table_name, items):
    """
        Function: add_items
         Purpose: Add items to dynamodb
        :returns: returns success message
    """
    client = dynamodb_client()
    response = client.put_item(
        TableName=table_name,
        Item=items,
    )
    print(response)
    return response


def list_table_items(table_name):
    resource = dynamodb_resource()
    table = resource.Table(table_name)
    summary = table.query()
    # # print(summary)
    return summary

def query_document(bucket, document, region):
    # Analyze the document
    client = boto3.client('textract', region_name=region)



    response = client.analyze_document(Document={'S3Object': {'Bucket': bucket, 'Name': document}},
                                       FeatureTypes=["FORMS"]
                                       )

    doc = Document(response)
    for page in doc.pages:
                # Print fields
                id = str(random.randint(1000,10000000))
                json_doc = json.loads('{}')
                json_doc.update({"id": {"S":f"{id}"}})
                for field in page.form.fields:
                    json_doc.update({
                        f"{field.key}": {"S":f"{field.value}"}})
    return json.dumps(json_doc)