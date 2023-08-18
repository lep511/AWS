"""
Sample Config file in AWS to make advanced queries:

SELECT
*
WHERE
resourceType = 'AWS::EC2::Subnet'

"""

import boto3
import json
from botocore.exceptions import ClientError

regionList = ['us-east-1'] #, 'us-west-2', 'eu-west-1']

def main():

    for region in regionList:
        config = boto3.client('config', region_name=region)
        paginator = config.get_paginator('select_resource_config')
        try:
            iterator = paginator.paginate(
                Expression="SELECT * WHERE resourceType = 'AWS::EC2::Subnet'",
                Limit=60,
            )
            for page in iterator:
                for resource in page['Results']:
                    resource = json.loads(resource)
                    print("Instance ID:", resource['resourceId'])
                    print("Region:", resource['awsRegion'])
                    print("arn:", resource['arn'])
                    print("---------------------------------")
        except ClientError as e:
            print(f"Error in region {region} with message: \n{e}")

if __name__ == '__main__':
    main()