import boto3
import cfnresponse
import json
import logging

def handler(event, context):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    responseData = {}
    responseStatus = cfnresponse.FAILED
    logger.info('Received event: {}'.format(json.dumps(event)))
    if event["RequestType"] == "Delete":
        responseStatus = cfnresponse.SUCCESS
        cfnresponse.send(event, context, responseStatus, responseData)
    if event["RequestType"] == "Create":
        try:
            Az1 = event["ResourceProperties"]["Az1"]
            FwArn = event["ResourceProperties"]["FwArn"]
        except Exception as e:
            logger.info('AZ retrieval failure: {}'.format(e))
        try:
            nfw = boto3.client('network-firewall')
        except Exception as e:
            logger.info('boto3.client failure: {}'.format(e))
        try:
            NfwResponse=nfw.describe_firewall(FirewallArn=FwArn)
            VpceId1 = NfwResponse['FirewallStatus']['SyncStates'][Az1]['Attachment']['EndpointId']

        except Exception as e:
            logger.info('ec2.describe_firewall failure: {}'.format(e))

        responseData['FwVpceId1'] = VpceId1
        responseStatus = cfnresponse.SUCCESS
        cfnresponse.send(event, context, responseStatus, responseData)