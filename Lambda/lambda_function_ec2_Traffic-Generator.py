"""
This lambda function generates login logs
"""
import os, json
import boto3
import logging
import requests

# It is a good practice to use proper logging.
# Here we are using the logging module of python.
# https://docs.python.org/3/library/logging.html

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Importing EC2 boto3 client and resources.
# For additional info: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#client
ec2_client = boto3.client('ec2')
ec2_resource = boto3.resource('ec2')

def lambda_handler(event, context):
    logger.info(event)
    
    instance_id = os.environ['instance_id']
    pub_ip = get_instances_pub_ip(instance_id)
    
    url = f"http://{pub_ip}:8443/"
    print(url)
    for num in range(40):
        response = requests.post(url,data="username=admin&password=test123")
        print(response)


def get_instances_pub_ip(instance_id):
    """
    This function gets public IP of the instance.
    """
    get_instances = ec2_client.describe_instances(InstanceIds=[instance_id])
    instances = get_instances['Reservations'][0].get('Instances')
    print(instances)
    for instance in instances:
        pub_ip = instance['PublicIpAddress']
        print(pub_ip)
    return pub_ip
    