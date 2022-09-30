import boto3
import os
import json
import logging
from datetime import datetime
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):

    dynamodbARN = os.environ['DynamodbArn']
    snsARN = os.environ['SnsArn']
    flowLogsLogGroupPrefix = os.environ['FlowLogsLogGroupPrefix']
    flowLogsDeliveryRoleArn=os.environ['FlowLogsDeliveryRoleArn']
    accountId = os.environ['AccountId']
    
    # Fetch all VPCs
    try:
        ec2_client = boto3.client('ec2')
        response = ec2_client.describe_vpcs(
            Filters=[
                {
                    'Name': 'owner-id',
                    'Values': [
                        accountId,
                    ]
                },
            ],
        )
        vpcs = response['Vpcs']
    except Exception as e:
        logger.info("Unexpected error: %s" % e)
        raise e

    for vpc in vpcs:
        # Recreate FlowLogs
        try:
            vpcId = vpc['VpcId']
            flowLogsLogGroupName = f'{flowLogsLogGroupPrefix}-{vpcId}'
            
            ec2_client = boto3.client('ec2')
            response = ec2_client.create_flow_logs(
                ResourceIds=[vpcId],
                ResourceType='VPC',
                TrafficType='ALL',
                LogGroupName=flowLogsLogGroupName,
                DeliverLogsPermissionArn=flowLogsDeliveryRoleArn,
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'FlowLogAlreadyExists':
                logger.info("WARNING: FlowLogAlreadyExists")
            else:
                logger.info("Unexpected error: %s" % e)
                raise e
        except Exception as e:
            logger.info("Unexpected error: %s" % e)
            raise e

    # Write event to DynamoDB Security Event-Log
    try:
        securityEventsTable = boto3.resource('dynamodb', region_name='us-west-2').Table(os.environ['DynamodbTableName'])
        securityEventsTable.put_item(
            Item = {
                'AccountId': event['account'],
                'EventRegion': event['region'],
                'EventId': event['id'],
                'EventSource': event['source'],
                'EventName': event['detail']['eventName'],
                'EventType': event['detail']['eventType'],
                'EventSessionIssuerType': event['detail']['userIdentity']['type'],
                'EventSessionIssuerPrincipleId': event['detail']['userIdentity']['principalId'],
                'EventSessionIssuerArn': event['detail']['userIdentity']['arn'],
                'EventSessionIssuerAccountId': event['detail']['userIdentity']['accountId'],
                'EventCapturedTime': datetime.utcnow().replace(microsecond=0).isoformat(),
                'EventFull': str(event),
                'Severity': "Critical",
                'RemidiationAction': 'FlowLogs Reactivation for Single Account VPC',
                'RemidiationActionTaker': 'Lambda',
                'RemidiationActionStatus': 'Finished',
                'NotificationAction': 'SNS-Topic',
                'NotificationActionDescription': 'Notification via SNS - True',
                'NotificationActionTime': datetime.utcnow().replace(microsecond=0).isoformat()
            }
        )  
    except Exception as e:
        logger.info("Unexpected DynamoDB error: %s" % e)
        raise e
         
    # Publish Event to SNS   
    try: 
        snsclient = boto3.client('sns', region_name='us-west-2')
        subject = "AutoMitigation Triggered - FlowLogs re-activated"
        message = "The FlowLogs for the VPC X were re-activated after they were turned off."
        snspublish = snsclient.publish(
            TargetArn= os.environ['SnsArn'],
            Subject=subject,
            Message=message)
    except Exception as e:
        logger.info("Unexpected SNS error: %s" % e)
        raise e

    return