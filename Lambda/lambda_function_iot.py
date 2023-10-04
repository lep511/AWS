# The above code is importing the necessary libraries for the code to run.
import boto3
import json
import base64
import uuid
from datetime import datetime
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Amazon Rekognition client
rekognition = boto3.client('rekognition')

# AWS IoTDataPlane client
iot_data_client = boto3.client('iot-data')

# Amazon DynamoDB table 
ddb_table = boto3.resource('dynamodb').Table('smart_door_log')

# Topic
topic = 'smart_door/actuator'

def log(result):
    """
    > This function takes a result as an argument, generates a UUID, gets the current time, and then
    puts an item in the DynamoDB table with the UUID, current time, and result
    
    :param result: The result of the function
    """
    try:
        myuuid = uuid.uuid4()
        now = datetime.now()
        current_time = now.strftime("%d/%m/%Y %H:%M:%S")
        ddb_table.put_item(
            Item={
                'id': str(myuuid),
                'time': current_time,
                'result': result,
            }
        )
    except Exception as e: 
        print("An exception occurred")
        print(e)
        raise

def lambda_handler(event, context):
    """
    > The function receives an image as a base64 encoded string, calls Amazon Rekognition to detect the
    presence of a face mask, and publishes the result to an AWS IoT topic
    
    :param event: The event that triggered the lambda function. In this case, it's the image that was
    sent to the S3 bucket
    :param context: The runtime information of the Lambda function that is executing
    :return: The result of the Rekognition call is being returned.
    """
    byte = str.encode(event['data'])
    # Call Amazon Rekognition
    response = rekognition.detect_protective_equipment(
         Image={
            'Bytes': base64.b64decode(byte)
        },
        SummarizationAttributes={
            'MinConfidence': 90,
            'RequiredEquipmentTypes': [
                'FACE_COVER'
            ]
        }
    )

    if (len(response["Summary"]["PersonsWithRequiredEquipment"]) > 0):
        result = "granted"
    else:
        result = "denied"

    iot_data_client.publish(
        topic=topic,
        qos=1,
        payload=json.dumps({"permission":result})
    )
    logger.info(json.dumps({"permission":result}))
    log(result)
    
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }