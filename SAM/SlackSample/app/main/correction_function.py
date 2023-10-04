# Role Policy:
"""
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "ec2:*",
                "ec2:Describe*",
                "ec2:ModifyInstanceAttribute"
            ],
            "Resource": "*",
            "Effect": "Allow"
        }
    ]
}
"""

import json
import boto3

ec2_client = boto3.client('ec2')

def lambda_handler(event, context):
    try:
        findings = event['detail']['findings']
        SecurityGroupId = "sg-08d6b9bc01a603d92"
        instanceARN = None

        if findings and len(findings) > 0:
            instanceARN = findings[0]['Resources'][0]['Id']

        instance_id = instanceARN.split('/')[1]

        response = ec2_client.modify_instance_attribute(
            InstanceId=instance_id,
            Groups=[SecurityGroupId]
        )

        return 'Grupo de seguridad actualizado.'
    except Exception as e:
        print('Error:', str(e))
        raise e
