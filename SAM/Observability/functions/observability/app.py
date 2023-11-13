import boto3
import json
import os
import uuid
from datetime import datetime
from aws_lambda_powertools import Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

tracer = Tracer()  # Sets service via POWERTOOLS_SERVICE_NAME env var

table_name = os.environ['TABLE_NAME']
bucket_name = os.environ['BUCKET_NAME']
dynamodb_client = boto3.client('dynamodb')

@tracer.capture_lambda_handler
def lambda_handler(event, context):
    event_type = event['requestContext']['http']['method']
    msg, scode = process_event(event_type, event)

    return {
        'statusCode': scode,
        'body': json.dumps(msg)
    }

@tracer.capture_method(capture_response=False)
def process_event(event_type, event):
    tracer.put_annotation(key="EventType", value=event_type)
    if event_type == 'PUT':
        try:
            message = json.loads(event['body'])
            logger.info('## PUT Event')
            logger.info(message)
            # Save the event to S3
            save_to_s3(message)
               
            response = push_to_dynamoDB(message)
            if response:
                return f"Item {message['id']} processed successfully", 200
            else:
                return f"Item {message['id']} not processed", 400
        except Exception as e:
            logger.error(e)
            return "Something went wrong", 500
    
    elif event_type == 'GET':
        try:
            id_item = event['queryStringParameters']['id']
            response = get_from_dynamoDB(id_item)
            if response:
                msg = {
                    "id": response['id']['S'],
                    "event": response['event']['S'],
                    "timestamp": response['timestamp']['S'],
                    "user_id": response['user_id']['S'],
                    "product_id": response['product_id']['S'],
                    "quantity": int(response['quantity']['N']),
                    "total_price": int(response['total_price']['N']),
                    "payment_method": response['payment_method']['S']
                }
                return msg, 200
            else:
                return "Item not found", 404
        except Exception as e:
            logger.error(e)
            return "Something went wrong", 500

@tracer.capture_method(capture_response=False)
def save_to_s3(event):
    try:
        # Generate a version 4 UUID
        uuid_value = uuid.uuid4()

        # Get the current date in the format "yyyyMMdd"
        current_date = datetime.now().strftime("%Y%m%d")
        # Remove hyphens from the UUID and combine it with the date to create a filename
        uuid_without_hyphens = str(uuid_value).replace("-", "")
        path = "events/sales"
        filename = f"{path}/{current_date}-{uuid_without_hyphens}.json"
        tracer.put_metadata(key="fileName", value=filename)
        
        s3_client = boto3.client('s3')
        s3_client.put_object(
            Body=json.dumps(event),
            Bucket=bucket_name,
            Key=filename
        )

    except Exception as e:
        logger.error(e)
        return False

    else:
        logger.info(f"File {filename} saved to S3")
        return True
    
@tracer.capture_method(capture_response=False)
def get_from_dynamoDB(id_item):
    try:
        response = dynamodb_client.get_item(
            TableName = table_name,
            Key = {
                'id': {'S': id_item}
            }
        )
    
    except Exception as e:
        logger.error(e)
        return False
    
    else:
        if 'Item' in response:
            logger.info(f"Item {id_item} retrieved from DynamoDB")           
            return response['Item']
        else:
            return False
        
@tracer.capture_method(capture_response=False)
def push_to_dynamoDB(message):

    try:
        item_data = {
            'id': {'S': message['id']},
            'event': {'S': message['event']},
            'timestamp': {'S': message['timestamp']},
            'user_id': {'S': message['user_id']},
            'product_id': {'S': message['product_id']},
            'quantity': {'N': str(message['quantity'])},
            'total_price': {'N': str(message['total_price'])},
            'payment_method': {'S': message['payment_method']}
        }

        response = dynamodb_client.put_item(
                        TableName = table_name, 
                            Item=item_data
                )
    
    except Exception as e:
        logger.error(e)
        return False
    
    else:
        logger.info(f"Item {message['id']} pushed to DynamoDB")
        return True
