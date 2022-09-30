"""
This Lambda function returns IAM and Security Group resources 
to compliance if drift is detected in CloudFormation stack.
"""
import os
import json
import logging
import time
import boto3

# It is a good practice to use proper logging.
# Here we are using the logging module of python.
# https://docs.python.org/3/library/logging.html

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Define CloudFormation stack information
STACK_NAME = "Enter_your_stack_name"
ROLE_NAME = os.environ['role_name']

# Importing IAM and CloudFormation boto3 client.
# For additional info: https://boto3.amazonaws.com/v1/documentation/api/latest/index.html

cloudformation_client = boto3.client('cloudformation')
iam_client = boto3.client('iam')


def repair_security_groups(resource_id,expected_value, actual_value):
    """Repair SG updates"""
    allowed_IpPermissions = [
        {
            "IpProtocol": "tcp",
            "FromPort": 22,
            "ToPort": 22,
            "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
        },
        {
            "IpProtocol": "tcp",
            "FromPort": 80,
            "ToPort": 80,
            "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
        }
    ]
    
    if expected_value != actual_value:
        ec2 = boto3.client('ec2')
        # Update SG rules
        print(expected_value)
        print(actual_value)
        response_SG = ec2.describe_security_groups(
                GroupIds=[resource_id]
            )
        current_IpPermissions = response_SG["SecurityGroups"][0].get('IpPermissions')
        logger.info(response_SG["SecurityGroups"][0].get('IpPermissions'))
        ec2.revoke_security_group_ingress(GroupId=resource_id,IpPermissions=current_IpPermissions)
        ec2.authorize_security_group_ingress(GroupId=resource_id, IpPermissions=allowed_IpPermissions)
        logger.info(f"Configuration restored for the security group with id {resource_id}")
    else:
        logger.info(f"No updates for the security group with id {resource_id}")
        

def repair_instance_profile(resource_id,expected_value, actual_value):
    """Repair instance profiles attached to EC2"""
    if expected_value != actual_value:
        
        ec2 = boto3.client('ec2')
        iam = boto3.client('iam')
        
        response_list_profiles = iam.list_instance_profiles(PathPrefix='/')
        # Iterate to get the approved instance profile ARN
        for profile in response_list_profiles['InstanceProfiles']:
            if expected_value in profile['InstanceProfileName']:
                approved_profile_arn = profile['Arn']
                logger.info(approved_profile_arn)
        
        
        #Get Association ID of the profile
        response_ec2_profile = ec2.describe_iam_instance_profile_associations(
                                        Filters=[
                                                    {
                                                        'Name': 'instance-id',
                                                        'Values': [resource_id]
                                                    }
                                                ]
                                        )
        # If the association is empty, update with approved profile
        # Else dissociate the unapproved profile and attach approved
        # instance profile.
        if not response_ec2_profile['IamInstanceProfileAssociations']:
            print("Empty")
            
            #Associate approved instance profile
            response_profile_associate = ec2.associate_iam_instance_profile(
                                            IamInstanceProfile={
                                                'Arn': approved_profile_arn,
                                                'Name': expected_value
                                            },
                                            InstanceId=resource_id
                                        )
            logger.info(response_profile_associate)
            logger.info(f"Instance Profile restored for the instance {resource_id}")
        else:
            associations = response_ec2_profile['IamInstanceProfileAssociations']
            association_id = associations[0]['AssociationId']
            logger.info(f"Association_ID:{association_id}")
        
            #Disassociate instance profile
            response_profile_disassociate = ec2.disassociate_iam_instance_profile(
                            AssociationId=association_id
                        )
            logger.info(response_profile_disassociate)
            
            #Associate approved Instance profile
            response_profile_associate = ec2.associate_iam_instance_profile(
                                            IamInstanceProfile={
                                                'Arn': approved_profile_arn,
                                                'Name': actual_value
                                            },
                                            InstanceId=resource_id
                                        )
            logger.info(response_profile_associate)
            logger.info(f"Instance Profile restored for the instance {resource_id}")
    else:
        logger.info(f"No instance profile update needed for the instance {resource_id}")


def lambda_handler(event, context):
    """Handle Lambda invocations from CloudWatch"""

    logger.info(event)
    # Initiate a stack drift detection

    initiate_stack_drift_detection = cloudformation_client.detect_stack_drift(
                StackName=STACK_NAME
    )
    stack_drift_detection_id = initiate_stack_drift_detection["StackDriftDetectionId"]
    logger.info("Initiating drift detection.  Stack Drift Detection Id: %s",
                stack_drift_detection_id)

    # Wait for the stack drift detection to complete
    drift_detection_status = ""
    while drift_detection_status not in ["DETECTION_COMPLETE",  "DETECTION_FAILED"]:
        check_stack_drift_detection_status = cloudformation_client.describe_stack_drift_detection_status(
            StackDriftDetectionId=stack_drift_detection_id
        )
        drift_detection_status = check_stack_drift_detection_status["DetectionStatus"]
        # Add artificial delay to avoid throttling by CloudFormation APIs
        time.sleep(1)
    logger.info("Drift detection complete. Stack Drift Status: %s", drift_detection_status)

    if drift_detection_status == "DETECTION_FAILED":
            logger.info("The stack drift detection did not complete successfully for at \
                         least one resource. Results will be available for resources that \
                         successfully completed drift detection")

    # Check if the stack has drifted
    if check_stack_drift_detection_status["StackDriftStatus"] == "DRIFTED":
        # Retrieve resources that have drifted
        stack_resource_drift = cloudformation_client.describe_stack_resource_drifts(
            StackName=STACK_NAME
        )
        
        logger.info("Drifted stack resources: %s", str(stack_resource_drift))

        # Iterate over drifted resources and return to compliance
        for drifted_stack_resource in stack_resource_drift["StackResourceDrifts"]:
            """
            Get resource type, resource id, expected resource configurations 
            and detected drift configurations
            """
            resource_type = drifted_stack_resource["ResourceType"]
            resource_id = drifted_stack_resource["PhysicalResourceId"]
            expected_properties = json.loads(drifted_stack_resource["ExpectedProperties"])
            actual_properties = json.loads(drifted_stack_resource["ActualProperties"])
            
            # Roll back the security group to standard allowed rules
            try:
                if resource_type =="AWS::EC2::SecurityGroup":
                    repair_security_groups(resource_id, expected_properties.get("SecurityGroupIngress", []),
                                        actual_properties.get("SecurityGroupIngress", []))
            except Exception as e:
                print(e)
            
            # Roll back the attached instance profile of the EC2 instance to allowed instance profile
            # try:
            #     if resource_type == "AWS::EC2::Instance":
            #         repair_instance_profile(resource_id,expected_properties.get("IamInstanceProfile", []),
            #                                 actual_properties.get("IamInstanceProfile", []))
            # except Exception as e:
            #     print(e)
    else:
        logger.info("No drift detected")