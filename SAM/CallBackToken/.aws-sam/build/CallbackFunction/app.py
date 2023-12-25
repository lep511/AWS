import json
import boto3
from botocore.exceptions import ClientError

stepfunctions = boto3.client('stepfunctions')

def lambda_handler(event, context):
    rep_body = "All tokens processed successfully."
    resp_code = 200
    
    print(event)
    for record in event['Records']:
        message_body = json.loads(record['body'])
        task_token = message_body['TaskToken']
        
        try:
            response = stepfunctions.send_task_success(    
                                                taskToken=task_token,
                                                output='"Callback task completed successfully."'
            )
            print(response)
        
        except ClientError as e:
            print(e)
            response = stepfunctions.send_task_failure(
                                                taskToken=task_token,
                                                error=str(e),
                                                cause='Error'
            )
            print(response)
            resp_body = "Error processing tokens."
            resp_code = 500
            
    
    return {
        'statusCode': resp_code,
        'body': json.dumps(rep_body)
    }