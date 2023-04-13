'''
This Lambda Function starts all the Glue workflows.
'''
import json
import os
import logging


import urllib3
http = urllib3.PoolManager()
SUCCESS = "SUCCESS"
FAILED = "FAILED"

responseData = {'status': 'NONE'}

# It is a good practice to use proper logging.
# Here we are using the logging module of python.
# https://docs.python.org/3/library/logging.html

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Import Boto 3 for AWS Glue
import boto3
client = boto3.client('glue')

# Variables for the job: 
glue_workflow_name = "s3_to_redshift"
glue_trigger_name = "glueTrigger"
s3_workflow_name = os.environ['S3WorkflowName']

# Define Lambda function
def lambda_handler(event, context):
    logger.info('## INITIATED BY EVENT: ')
    logger.info(json.dumps(event))

    response_list_workflows = client.list_workflows()
    logger.info(json.dumps(response_list_workflows))
    workflow_list = response_list_workflows.get('Workflows')

    try:
        if event['RequestType'] == 'Create' or event['RequestType'] == 'Update':
            try:
                startWorkFlow(s3_workflow_name)
                responseData['status'] = 'STARTED WORKFLOW'
                send(event, context, SUCCESS, responseData ,physicalResourceId=event['LogicalResourceId'])
            except Exception as e:
                logger.info(f"Error: {e}")
                responseData['status'] = f'FAILED TO START WORKFLOW. ERROR {e}'
                send(event, context, SUCCESS, responseData ,physicalResourceId=event['LogicalResourceId'])
        elif event['RequestType'] == 'Delete':
            responseData['status'] = f'DELETE IN PROGRESS'
            send(event, context, SUCCESS, responseData ,physicalResourceId=event['LogicalResourceId'])
    except Exception as e:
        logger.info(f"Error: {e}")
        try:
            print(workflow_list)
            workflow_list.remove(s3_workflow_name)
            print(workflow_list)
            for workflow in workflow_list:
                startWorkFlow(workflow)
        except Exception as e:
            logger.info(f"Error: {e}")
            result = {"Status": "Failed", "Message": "Did you create new workflow?"}
            logger.info(result)
            return result

def startWorkFlow(workflow_name):
    response_start_workflow = client.start_workflow_run(Name=workflow_name)
    logger.info('## STARTED WORKFLOW JOB: ' + workflow_name)
    logger.info(json.dumps(response_start_workflow))

def send(event, context, responseStatus, responseData, physicalResourceId=None, noEcho=False, error=None):
    responseUrl = event['ResponseURL']

    logger.info(responseUrl)

    responseBody = {}
    responseBody['Status'] = responseStatus
    if error is None: 
        responseBody['Reason'] = 'See the details in CloudWatch Log Stream: ' + context.log_stream_name + ' LogGroup: ' + context.log_group_name
    else:
        responseBody['Reason'] = error
    responseBody['PhysicalResourceId'] = physicalResourceId or context.log_stream_name
    responseBody['StackId'] = event['StackId']
    responseBody['RequestId'] = event['RequestId']
    responseBody['LogicalResourceId'] = event['LogicalResourceId']
    responseBody['NoEcho'] = noEcho
    responseBody['Data'] = responseData

    json_responseBody = json.dumps(responseBody)

    print("Response body:\n" + json_responseBody)

    headers = {
        'content-type' : '',
        'content-length' : str(len(json_responseBody))
    }
    try:
        response = http.request('PUT',responseUrl,body=json_responseBody.encode('utf-8'),headers=headers)
        print("Status code: " + response.reason)
    except Exception as e:
        print("send(..) failed executing requests.put(..): " + str(e))
