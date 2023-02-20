# This Lambda function enables WAF web ACLs logging.
import boto3
import json
import os
import cfnresponse

FIREHOSE_ARN = os.environ['FIREHOSE_ARN']
WEBACL = os.environ['WEBACL']

def handler(event, context):
  if event['RequestType'] == 'Delete':
    responseData = {}      
    cfnresponse.send(event, context, cfnresponse.SUCCESS, responseData)
    return

  hasConfig = False

  #Setting up variables
  client = ''
  response = ''
  wafArn = ''

  wafArn = WEBACL
  client = boto3.client('wafv2')

  try:
    response = client.get_logging_configuration(ResourceArn=wafArn)
    hasConfig = True
  except:
    print('Attempting to enable logging')
    print('WAF ARN: ' + wafArn)
    response = client.put_logging_configuration(LoggingConfiguration={'ResourceArn': wafArn,'LogDestinationConfigs': [ FIREHOSE_ARN ]})

  responseData = {}
  cfnresponse.send(event, context, cfnresponse.SUCCESS, responseData)
  return
