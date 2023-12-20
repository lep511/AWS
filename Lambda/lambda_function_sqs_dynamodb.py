import boto3

dynamodb_client = boto3.client('dynamodb')

DDB_TABLE = 'ProcessedRecords'

# Validates if the message is already processed in previous invokes.
# @input string message_id
#
# @param message_id used to query the message from DynamoDB
# @return Boolean
def is_duplicate_message(message_id):
    return dynamodb_client.query(
        TableName='ProcessedRecords',
        Select='COUNT',
        KeyConditionExpression='Records = :Records',
        ExpressionAttributeValues={
            ':Records': {'S': message_id}
        }
    )["Count"] != 0
    
# Processes the message body to upper case.
# @input string body
#
# @param body to be processed
# @return uppercase body
def process_message(body):
    return body.upper()

# Put the message to the DynamoDB Table.
# @input string batch_item_success
#
# @param batch_item_success of the message to put.
# @return Boolean
def push_to_dynamoDB(batch_item_success):
    
    for message_id in batch_item_success:
        response = dynamodb_client.put_item(
                        TableName = DDB_TABLE, 
                        Item={ 'Records': {'S':message_id}
                        }
                    )
    return True

# processor function iterating through messages in the event.
# @input dict Records
#
# @param Records to be processed
# @return Boolean
def iterate_records(Records):
    
    batch_item_failures = []
    batch_item_success = []
    
    for record in Records:
        
        message_id = record["messageId"]
        print("Message: " + message_id)
        if is_duplicate_message(message_id):   
            print("Message duplicate: " + message_id)
            continue
        
        try:
            process_message(record["body"])
            batch_item_success.append(message_id) 
        except:
            batch_item_failures.append({"itemIdentifier": message_id}) 
    
    push_to_dynamoDB(batch_item_success)
    return batch_item_failures
    
def lambda_handler(event, context):
    
    return iterate_records(event["Records"])