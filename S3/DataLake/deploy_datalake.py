import boto3
import argparse
import time
from botocore.exceptions import ClientError

parser = argparse.ArgumentParser(description='Deploy Data Lake')
parser.add_argument('--region', type=str, default='us-east-1', help='AWS region to create S3 bucket (default: us-east-1)')
parser.add_argument('--profile', type=str, default='default', help='AWS profile (default: default)')
parser.add_argument('--lz', type=str, default='true', help='Create landing zone bucket (default: true)', choices=['true', 'false'])
parser.add_argument('--env', type=str, default='dev', help='Environment e.g. dev, test, prod - (default: dev)')
parser.add_argument('--company', type=str, required=False, help='Company name in lowecase with no spaces e.g. mycompany (default: None)')
parser.add_argument('--versioning', type=str, default='true', help='Enable versioning on buckets (default: true)', choices=['true', 'false'])

args = parser.parse_args()
region = args.region
profile = args.profile
lz = args.lz
env = args.env
versioning = args.versioning
company = args.company

try:
    session = boto3.Session(profile_name=profile)
except ClientError as e:
    raise Exception(f'Error creating boto3 session: {e}')

if lz in ['true', 'True', 'TRUE']:
    lz = True
else:
    lz = False
    
if versioning in ['true', 'True', 'TRUE']:
    versioning = True
else:
    versioning = False

def bucket_exists(bucket_name, session):
    """
    Checks if an S3 bucket exists.

    Args:
    bucket_name: The name of the bucket to check.

    Returns:
    True if the bucket exists, False otherwise.
    """

    s3_client = session.client('s3')
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        return True
    except ClientError as e:
        return False

def enable_versioning(session, lz_bucket_name, rw_bucket_name, st_bucket_name, an_bucket_name):
    # Enable Versioning on Landing Zone Bucket
    s3_client = session.client('s3', region_name=region)
    
    if lz_bucket_name and lz_bucket_name != '[SKIPPED]' and lz_bucket_name != '[EXISTS]':
        try:
            print('Enabling versioning on landing zone bucket...')
            response = s3_client.put_bucket_versioning(
                Bucket=lz_bucket_name,
                VersioningConfiguration={
                    'Status': 'Enabled'
                }
            )
        except ClientError as e:
            print(f'[ERROR] Error enabling versioning on landing zone bucket: {e}')

    # Enable Versioning on Raw Data Bucket
    if rw_bucket_name and rw_bucket_name != '[EXISTS]':
        try:
            print('Enabling versioning on raw data bucket...')
            response = s3_client.put_bucket_versioning(
                Bucket=rw_bucket_name,
                VersioningConfiguration={
                    'Status': 'Enabled'
                }
            )
        except ClientError as e:
            print(f'[ERROR] Error enabling versioning on raw data bucket: {e}')
            
    # Enable Versioning on Stage Data Bucket
    if st_bucket_name and st_bucket_name != '[EXISTS]':
        try:
            print('Enabling versioning on stage data bucket...')
            response = s3_client.put_bucket_versioning(
                Bucket=st_bucket_name,
                VersioningConfiguration={
                    'Status': 'Enabled'
                }
            )
        except ClientError as e:
            print(f'[ERROR] Error enabling versioning on stage data bucket: {e}')
    
    # Enable Versioning on Analytics Data Bucket
    if an_bucket_name and an_bucket_name != '[EXISTS]':
        try:
            print('Enabling versioning on analytics data bucket...')
            response = s3_client.put_bucket_versioning(
                Bucket=an_bucket_name,
                VersioningConfiguration={
                    'Status': 'Enabled'
                }
            )
        except ClientError as e:
            print(f'[ERROR] Error enabling versioning on analytics data bucket: {e}')


##############################################
# Main Function
##############################################
def create_datalake(session, lz, region, versioning=True, env='dev', company=None):
    
    s3_client = session.client('s3', region_name=region)
    sts_client = session.client('sts')
    region_abr = region.replace('-', '')
    account_id = sts_client.get_caller_identity()['Account']
    
    ##########################################
    # Landing Zone Bucket
    ##########################################
    if lz:
        if company:
            lz_bucket_name = f'{company}-landingzone-{region_abr}-{account_id}-{env}'
        else:
            lz_bucket_name = f'landingzone-{region_abr}-{account_id}-{env}'

        # Check if bucket exists
        if bucket_exists(lz_bucket_name, session):
            print(f'[ERROR] Bucket exists: {lz_bucket_name}')
            lz_bucket_name = '[EXISTS]'
        else:
            try:
                print('Creating landing zone bucket...')
                if region == 'us-east-1':
                    response = s3_client.create_bucket(
                        Bucket=lz_bucket_name, 
                    )
                else:
                    response = s3_client.create_bucket(
                        Bucket=lz_bucket_name,
                        CreateBucketConfiguration={
                            'LocationConstraint': region
                        }  
                    )

            except ClientError as e:
                print(f'[ERROR] Error creating landing zone bucket: {e}')
                lz_bucket_name = None
    else:
        lz_bucket_name = '[SKIPPED]'
    
    ##########################################
    # Raw Data Bucket
    ##########################################
    
    if company:
        rw_bucket_name = f'{company}-raw-{region_abr}-{account_id}-{env}'
    else:
        rw_bucket_name = f'raw-{region_abr}-{account_id}-{env}'
    
    # Check if bucket exists
    if bucket_exists(rw_bucket_name, session):
        print(f'[ERROR] Bucket exists: {rw_bucket_name}')
        rw_bucket_name = '[EXISTS]'
    else:
        try:
            print('Creating raw data bucket...')
            if region == 'us-east-1':
                response = s3_client.create_bucket(
                    Bucket=rw_bucket_name, 
                )

            else:
                response = s3_client.create_bucket(
                    Bucket=rw_bucket_name,
                    CreateBucketConfiguration={
                        'LocationConstraint': region
                    }  
                )
        except ClientError as e:
            print(f'[ERROR] Error creating raw data bucket: {e}')
            rw_bucket_name = None
        
    ##########################################
    # Stage Data Bucket
    ##########################################
    
    if company:
        st_bucket_name = f'{company}-stage-{region_abr}-{account_id}-{env}'
    else:
        st_bucket_name = f'stage-{region_abr}-{account_id}-{env}'
    
    # Check if bucket exists
    if bucket_exists(st_bucket_name, session):
        print(f'[ERROR] Bucket exists: {st_bucket_name}')
        st_bucket_name = '[EXISTS]'
    else:
        try:
            print('Creating stage data bucket...')
            if region == 'us-east-1':
                response = s3_client.create_bucket(
                    Bucket=st_bucket_name, 
                )
            else:
                response = s3_client.create_bucket(
                    Bucket=st_bucket_name,
                    CreateBucketConfiguration={
                        'LocationConstraint': region
                    }  
                )
        except ClientError as e:
            print(f'[ERROR] Error creating stage data bucket: {e}')
            st_bucket_name = None
    
    ##########################################
    # Analytics Data Bucket
    ##########################################
    
    if company:
        an_bucket_name = f'{company}-analytics-{region_abr}-{account_id}-{env}'
    else:
        an_bucket_name = f'analytics-{region_abr}-{account_id}-{env}'
    
    # Check if bucket exists
    if bucket_exists(an_bucket_name, session):
        print(f'[ERROR] Bucket exists: {an_bucket_name}')
        an_bucket_name = '[EXISTS]'
    else:
        try:
            print('Creating analytics data bucket...')
            if region == 'us-east-1':
                response = s3_client.create_bucket(
                    Bucket=an_bucket_name, 
                )

            else:
                response = s3_client.create_bucket(
                    Bucket=an_bucket_name,
                    CreateBucketConfiguration={
                        'LocationConstraint': region
                    }  
                )
        except ClientError as e:
            print(f'[ERROR] Error creating analytics data bucket: {e}')
            an_bucket_name = None

    ##########################################
    # Enable Versioning
    ##########################################
    if versioning:
        enable_versioning(session, lz_bucket_name, rw_bucket_name, st_bucket_name, an_bucket_name)
    
    return lz_bucket_name, rw_bucket_name, st_bucket_name, an_bucket_name
            

if __name__ == '__main__':
    print('### Deploying Data Lake ###')
    lz_b, rw_b, st_b, an_b = create_datalake(session, lz, region, versioning, env, company)
    print('\n--------------------------------------------------------')
    print(' * Landing Zone Bucket: ', lz_b) if lz_b else print(' * Landing Zone Bucket: [FAILED]')
    print(' * Raw Data Bucket: ', rw_b) if rw_b else print(' * Raw Data Bucket: [FAILED]')
    print(' * Stage Data Bucket: ', st_b) if st_b else print(' * Stage Data Bucket: [FAILED]')
    print(' * Analytics Data Bucket: ', an_b) if an_b else print(' * Analytics Data Bucket: [FAILED]')

    