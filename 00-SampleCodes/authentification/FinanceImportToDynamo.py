import json, boto3, os
import logging
import urllib3
http = urllib3.PoolManager()
SUCCESS = "SUCCESS"
FAILED = "FAILED"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client('dynamodb')

def lambda_handler(event, context):
  logger.info(json.dumps(event))
  responseData = {'status': 'NONE'}

  try:
    data = client.put_item(
      TableName='bank-data',
      Item={
          'LastName': {
            'S': 'Jackson'
          },
          'FirstName': {
            'S': 'Mateo'
          },
          'id': {
            'S': '56438794'
          },
          'CheckingBalance': {
            'S': '575.82'
          },
          'SavingsBalance': {
          'S': '10256.23'
          },
          'MortgageBalance': {
          'S': '255645.59'
          },
          'CCBalance': {
          'S': '74.25'
          }
      }
    )
    logger.info("Successfully created the record")
    responseData['status'] = "Successfully created the record"
    send(event, context, SUCCESS, responseData,physicalResourceId=event['LogicalResourceId'])

  except Exception as e:
    logger.info(f"Failed to create a record with following error: {e}")
    responseData['status'] = f"Failed to create a record with following error: {e}"
    send(event, context, SUCCESS, responseData ,physicalResourceId=event['LogicalResourceId'])
  



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
