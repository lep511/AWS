'''
This lambda codes copies file from source bucket to target bucket 
for CloudFormation CREATE or UPDATE events, and deletes target bucket  
and contents for CloudFormation DELETE event.
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
  s3 = boto3.resource('s3')
  s3_client = boto3.client('s3')
  responseData = {'status': 'NONE'}
  
# Get variables from the event (populated by the AWS CloudFormation trigger)
  sourceBucket = event['ResourceProperties'].get('sourceBucket')
  keyPrefix = event['ResourceProperties'].get('keyPrefix')
  destinationBucket = event['ResourceProperties'].get('destinationBucket')
  fileList = event['ResourceProperties'].get('fileList')
  logger.info(fileList)

  # If AWS CloudFormation triggers the function with CREATE or UPDATE, do the following
  if event['RequestType'] == 'Create' or event['RequestType'] == 'Update':
    # Designate what files need to be put in the Amazon S3 bucket
    for file in fileList:
      sourceKey = f"{keyPrefix}/{file}"
      sourceObject = { 'Bucket': sourceBucket, 'Key': sourceKey }
      try:
        # Copy the files to the Amazon S3 bucket
        s3.meta.client.copy(sourceObject, destinationBucket, file )
      except Exception as e:
        print(e)
        responseData['status'] = f'FAILED TO COPY. ERROR {e}'
        send(event, context, FAILED, responseData ,physicalResourceId=event['LogicalResourceId'])
    responseData['status'] = 'CREATED'
    send(event, context, SUCCESS, responseData,physicalResourceId=event['LogicalResourceId'])
  # If AWS CloudFormation triggers the function with DELETE, do the following
  elif event['RequestType'] == 'Delete':
    try:
        #List all the content of the destination bucket
        response_list_objects = s3_client.list_objects_v2(Bucket=destinationBucket)
        files_in_bucket = response_list_objects["Contents"]
        files_to_delete = []
        # Iterate through the list to delete all files
        if files_in_bucket:
            for file in files_in_bucket:
                files_to_delete.append({"Key": file["Key"]})
            # This will delete all files in a folder
            response = s3_client.delete_objects(
                Bucket=destinationBucket, Delete={"Objects": files_to_delete}
            )
        logger.info("Bucket is empty")
        responseData['status'] = f'DELETE S3 files COMPLETE.'
        send(event, context, SUCCESS, responseData ,physicalResourceId=event['LogicalResourceId'])
    except Exception as e:
        logger.info(e)
        responseData['status'] = f'FAILED TO DELETE FILES. ERROR: {e}'
        send(event, context, SUCCESS, responseData ,physicalResourceId=event['LogicalResourceId'])

### Uncomment the below lines if you want to delete the destination bucket. #####    
    # try:
    #     response_delete_s3 = s3_client.delete_bucket(Bucket=destinationBucket)
    #     logger.info(response_delete_s3)
    #     responseData['status'] = 'DELETE S3 COMPLETE'
    #     send(event, context, SUCCESS, responseData,physicalResourceId=event['LogicalResourceId'])
    # except Exception as e:
    #     logger.info(e)
    #     responseData['status'] = f'FAILED TO DELETE S3. ERROR: {e}'
    #     send(event, context, SUCCESS, responseData ,physicalResourceId=event['LogicalResourceId'])

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
        print("send(..) failed executing requests.put(..): " + str(e))S