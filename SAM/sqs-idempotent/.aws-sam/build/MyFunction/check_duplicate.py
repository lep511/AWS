import boto3
import os

def is_duplicate_message(message_id):
    dynamo = boto3.client('dynamodb')
    table_name = os.environ['PROCESSED_RECORDS']
    return dynamo.query(
        TableName=table_name,
        Select='COUNT',
        KeyConditionExpression='Records = :Records',
        ExpressionAttributeValues={
            ':Records': {'S': message_id}
        }
    )["Count"] != 0