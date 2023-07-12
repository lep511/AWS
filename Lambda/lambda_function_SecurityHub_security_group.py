import json
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    try:
        findings = event['detail']['findings']
        securitg_group_id = 'sg-0aa87f294afc53607'
        if len(findings) > 0:
            instance_arn = findings[0]['Resources'][0]['Id']
            instance_id = instance_arn.split('/')[1]
            ec2_client = boto3.client('ec2')
            ec2_client.modify_instance_attribute(
                InstanceId=instance_id,
                Groups=[
                    securitg_group_id
                ]
            )
            print("Updated security group.")
            return {
                "statusCode": 200,
                "body": json.dumps("Updated security group.")
            }
        else:
            print("No findings.")
            return {
                "statusCode": 202,
                "body": json.dumps("No findings.")
            }
    except ClientError as e:
        print("[ERROR] " + str(e))
        return {
            "statusCode": 500,
            "body": json.dumps("Error." + str(e))
        }   