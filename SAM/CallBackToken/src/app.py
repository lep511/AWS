import json
import boto3

stepfunctions = boto3.client('stepfunctions')

def lambda_handler(event, context):
    
    for record in event['Records']:
        message_body = json.loads(record['body'])
        task_token = message_body['TaskToken']
        
        try:
            response = stepfunctions.send_task_success(    
                                                taskToken=task_token,
                                                output='"Callback task completed successfully."'
            )
            print(response)
        except Exception as e:
            print(e)
            raise e
