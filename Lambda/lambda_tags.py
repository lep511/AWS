import boto3
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Set up EC2 client and SSM client
ec2_client = boto3.client('ec2')
ssm_client = boto3.client('ssm')

def lambda_handler(event, context):
    # Retrieve tags from SSM Parameter Store
    response = ssm_client.get_parameter(Name='/abc/apps/tags')
    tags = response['Parameter']['Value']

    # Convert tags from string to dictionary
    tags_dict = {}
    for tag in tags.split(','):
        key, value = tag.split('=')
        tags_dict[key] = value

    # Get list of EC2 instances
    response = ec2_client.describe_instances()

    # Apply tags to each instance
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            ec2_tags = []
            for key, value in tags_dict.items():
                ec2_tags.append({'Key': key, 'Value': value})
            ec2_client.create_tags(Resources=[instance['InstanceId']], Tags=ec2_tags)

    logger.info('Tags applied to all EC2 instances.')