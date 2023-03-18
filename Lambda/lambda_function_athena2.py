'''
This Lambda code updates primary workgroup output S3 location
of Athena Query editor.
'''

import json, boto3, os
import logging
import urllib3
http = urllib3.PoolManager()
SUCCESS = "SUCCESS"
FAILED = "FAILED"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context): 
    logger.info(json.dumps(event))
    responseData = {'status': 'NONE'}
    athena = boto3.client('athena')
    try:
        # If AWS CloudFormation triggers the function with CREATE, do the following
        if event['RequestType'] == 'Create':
        # Get variables from the event (populated by the AWS CloudFormation trigger)
            queryBucket = event['ResourceProperties'].get('queryBucket')

            client = boto3.client('athena')
            response = client.update_work_group(
                WorkGroup = 'primary',
                ConfigurationUpdates={
                    'ResultConfigurationUpdates': {
                        'OutputLocation': f"s3://{queryBucket}/queries/",
                        }
                }
            )
            print(response) 
        responseData['status'] = 'Workgroup updated'
        send(event, context, SUCCESS, responseData,physicalResourceId=event['LogicalResourceId'])
    except Exception as e:
        logger.info(f"Error: {e}")
        responseData['status'] = f'Workgroup not updated. ERROR {e}'
        send(event, context, FAILED, responseData ,physicalResourceId=event['LogicalResourceId'])

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