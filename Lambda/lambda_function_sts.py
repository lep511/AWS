import boto3
import time
import json
import logging
import os


#get environment variables
vpc_guid = os.environ['vpc_guid']
user_id = os.environ['lab_user_id']
secret_id = os.environ['secret_id']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    client = boto3.client('sts')
    response = client.get_caller_identity()
    account_id = response['Account']
    ds_name = f"supply-chain-lab-{account_id}"
    
    #retrieve secrets manager secret values
    secrets_client = boto3.client('secretsmanager')
    response = secrets_client.get_secret_value(SecretId=secret_id)
    secret = json.loads(response['SecretString'])
    password = secret['password']
    username = secret['username']
    database = secret['dbname']
    host = secret['host']
    port = secret['port']
    
    #create quicksight datasource from aurora database
    client = boto3.client('quicksight')
    response = client.create_data_source(
        AwsAccountId=account_id,
        Name=ds_name,
        Type='AURORA_POSTGRESQL',
        DataSourceId=ds_name,
        DataSourceParameters={
            'AuroraPostgreSqlParameters': {
                'Database': database,
                'Host': host,
                'Port': port
                }
        },
        Credentials={
            'CredentialPair': {
                'Username': username,
                'Password': password,
            }
        },
        VpcConnectionProperties={
            'VpcConnectionArn': f"arn:aws:quicksight:us-east-1:{account_id}:vpcConnection/{vpc_guid}"
        },    
        Permissions=[
            {
                'Principal': f"arn:aws:quicksight:us-east-1:{account_id}:user/default/{user_id}",
                'Actions': [
                    'quicksight:UpdateDataSourcePermissions', 
                    'quicksight:DescribeDataSourcePermissions', 
                    'quicksight:PassDataSource', 
                    'quicksight:DescribeDataSource', 
                    'quicksight:DeleteDataSource', 
                    'quicksight:UpdateDataSource'
                ]
            }
        ]
    )
    
    status = json.dumps(response['CreationStatus'],default=str)
    
    while status != '"CREATION_SUCCESSFUL"':
        logger.info("Data source creation in progress")
        response = client.describe_data_source(
            AwsAccountId=account_id,
            DataSourceId=ds_name
        )
        status = json.dumps(response['DataSource']['Status'], default=str)
        logger.info("Status = " + status)
        time.sleep(5)

    logger.info("Data source creation completed")
    
    return True