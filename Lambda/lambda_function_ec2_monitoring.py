import json, os
import boto3
from datetime import datetime
import urllib3
import random
import logging

http = urllib3.PoolManager()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info(event)

    max_instance = int(os.environ['maxInstance'])
    
    
    try:
        ec2_client = boto3.client('ec2')
        response_get_ec2_hosts = ec2_client.describe_instances(Filters=[{'Name': 'instance-type', 'Values': ["*"]}])
        
        print(json.dumps(response_get_ec2_hosts,default=str))
        
        ec2_list = []
        for item in response_get_ec2_hosts['Reservations']:
            for int_ids in item['Instances']:
                if (int_ids['State']['Name'] != 'terminated') and (int_ids['State']['Name'] != 'shutting-down'):
                    print(int_ids['InstanceId'])
                    print(int_ids['State']['Name'])
                    ec2_list.append(int_ids['InstanceId'])
                else:
                    pass
        
        logger.info(ec2_list)
        
        # Count number of EC2 instances in list and take action if the instances are more than max_instance.
        
        num = len(ec2_list)
        
        while num > max_instance:
            logger.info('time to delete')
            
            rand_num = random.randint(0,num-1)
            logger.info(rand_num)
            
            ## Delete the random EMR cluster
        
            response_ec2_delete = ec2_client.terminate_instances(
                                    InstanceIds=[
                                        ec2_list[rand_num],
                                    ],
                                    DryRun=False
                                )
            logger.info(response_ec2_delete)
            num -= num
            print(num)
        return "All instances more than max number deleted"

    except Exception as exp:
        logger.exception(exp)
