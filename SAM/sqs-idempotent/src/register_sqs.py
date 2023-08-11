import boto3
import os

def push_to_process_table(message_id):
    dynamo = boto3.client('dynamodb')
    table_name = os.environ['PROCESSED_RECORDS']
    try:
        response = dynamo.put_item(
                    TableName = table_name, 
                    Item={ 'Records': {'S':message_id}
                    }
                )
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            print("[ERROR]", e.response['Error']['Message'])
            return False
    except ClientError as e:
        print("[ERROR]", e.response['Error']['Message'])
        return False
    
    return True