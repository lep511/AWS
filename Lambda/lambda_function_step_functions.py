import time
import boto3
import json
import random


stepfunctions = boto3.client('stepfunctions')


def lambda_handler(event, context):
  time.sleep(3+random.randint(0,5))
  for record in event['Records']:
    body = json.loads(record['body'])
    task_token = body['TaskToken']
    params = {
        'output': 'Callback task completed successfully.',
        'task_token': task_token
    }
    print('Calling Step Functions to complete callback task with params {}'.format(params))
    try:
        stepfunctions.send_task_success(taskToken=task_token, output='{"output": "Callback task completed successfully."}')
    except Exception as e:
        stepfunctions.send_task_failure(taskToken=task_token, error='500', cause=repr(e))
        return { 'statusCode': 500,
          'body': {
            'updated': True
          }
        }
        
  return { 'statusCode': 200,
    'body': {
      'updated': True
    }
  }
