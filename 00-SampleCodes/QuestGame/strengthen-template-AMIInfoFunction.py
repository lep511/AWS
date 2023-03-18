import json
import boto3
import cfnresponse

def lambda_handler(event, context):
  if event['RequestType'] == 'Delete':
    responseData = {}      
    cfnresponse.send(event, context, cfnresponse.SUCCESS, responseData)
    return
  
  ec2=boto3.client('ec2')
  imageDescriptions=ec2.describe_images(
    Owners=['amazon'],
    Filters=[
      {'Name': 'name', 'Values': [event['ResourceProperties']['NameFilter']]}, 
      {'Name': 'architecture', 'Values': ['x86_64']}
    ],
  )
  
  numImageDescriptions = len(imageDescriptions['Images'])
  if numImageDescriptions < 2:
    responseData = {}
    cfnresponse.send(event, context, cfnresponse.FAILED, responseData)
  else:
    amiNames = sorted(imageDescriptions['Images'],
      key=lambda x: x['CreationDate'],
      reverse=True)
    responseData = {}
    responseData['Id'] = amiNames[0]['ImageId']
    cfnresponse.send(event, context, cfnresponse.SUCCESS, responseData)
  return
