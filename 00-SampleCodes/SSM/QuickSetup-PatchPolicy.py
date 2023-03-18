# Copyright 2022 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# Licensed under the Apache License, Version 2.0 (the 'License'). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#     http://aws.amazon.com/apache2.0/
# or in the 'license' file accompanying this file. This file is
# distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
#
# This handler performs CRUD operations on an S3 object.
# This handler also adds a Quick Setup specific bucket policy to the bucket
# to enable target nodes to pull down the S3 object during patching operations.


import boto3
import json
import urllib3
import time
import os


SUCCESS = 'SUCCESS'
FAILED = 'FAILED'

# Events sent in by CloudFormation
CREATE = 'Create'
UPDATE = 'Update'
DELETE = 'Delete'

# Event sent in by Automation
REMEDIATE = 'Remediate'

DEFAULT_REGION = 'us-east-1'

region = os.environ['REGION']
s3_client = boto3.client('s3', region_name=region)
ssm_client = boto3.client('ssm', region_name=region)
s3_resource = boto3.resource('s3', region_name=region)
http = urllib3.PoolManager()


def create_bucket(bucket_name):
    bucket_creation_params = {
        'ACL': 'private',
        'Bucket': bucket_name,
        'CreateBucketConfiguration': {
            'LocationConstraint': region
        },
        'ObjectOwnership': 'BucketOwnerEnforced'
    }

    if region == DEFAULT_REGION:
        del bucket_creation_params['CreateBucketConfiguration']
        print('Creating a bucket in', DEFAULT_REGION, '...', '\n')
    else:
        print('Creating a bucket in', region, '...', '\n')

    s3_client.create_bucket(**bucket_creation_params)
    waiter = s3_client.get_waiter('bucket_exists')
    waiter.wait(Bucket=bucket_name)
    print('Successfully created the bucket:', bucket_name, '\n')


def put_bucket_versioning(bucket_name):
    print('Enabling bucket versioning... \n')
    s3_client.put_bucket_versioning(
        Bucket=bucket_name,
        VersioningConfiguration={
            'MFADelete': 'Disabled',
            'Status': 'Enabled'
        }
    )
    print('Bucket versioning enabled \n')


def put_bucket_encryption(bucket_name):
    print('Applying server side encryption to the bucket... \n')
    s3_client.put_bucket_encryption(
        Bucket=bucket_name,
        ServerSideEncryptionConfiguration={
            'Rules': [
                {
                    'ApplyServerSideEncryptionByDefault': {
                        'SSEAlgorithm': 'AES256'
                    }
                }
            ]
        }
    )
    print('Encryption applied to the bucket \n')


def put_public_access_block(bucket_name):
    print('Turning on public access block for the bucket... \n')
    s3_client.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': True,
            'IgnorePublicAcls': True,
            'BlockPublicPolicy': True,
            'RestrictPublicBuckets': True
        }
    )
    print('Public access block turned on for the bucket \n')


def put_bucket_lifecycle_configuration(bucket_name):
    print('Applying lifecycle configuration to the bucket... \n')
    s3_client.put_bucket_lifecycle_configuration(
        Bucket=bucket_name,
        LifecycleConfiguration={
            'Rules': [
                {
                    'ID': 'DeleteVersionsOlderThan90Days',
                    'Filter': {
                        'Prefix': 'baseline_overrides.json'
                    },
                    'Status': 'Enabled',
                    'NoncurrentVersionExpiration': {
                        'NoncurrentDays': 90
                    }
                }
            ]
        }
    )
    print('Lifecycle configuration applied to the bucket \n')


def put_bucket_policy(bucket_name, resource_properties):
    print('Constructing and applying bucket policy... \n')
    partition = resource_properties['Partition']
    baseline_overrides_json = f'arn:{partition}:s3:::{bucket_name}/baseline_overrides.json'
    qs_configuration_id = resource_properties['QSConfigId']
    target_entities = resource_properties['TargetEntities']
    organizational_units = resource_properties['OrgUnits']
    principal_org_id = resource_properties['PrincipalOrgId']
    account_id = resource_properties['AccountId']

    bucket_policy = {
        'Version': '2012-10-17',
        'Statement': [
            {
                'Sid': 'DenyInsecureTransport',
                'Effect': 'Deny',
                'Principal': '*',
                'Action': 's3:*',
                'Resource': [
                    f'arn:{partition}:s3:::{bucket_name}/*'
                ],
                'Condition': {
                    'Bool': {
                        'aws:SecureTransport': 'false'
                    }
                }
            },
            {
                'Sid': 'DenyAllButPrincipalsWithTag',
                'Effect': 'Deny',
                'Principal': {
                    'AWS': '*'
                },
                'Action': 's3:GetObject',
                'Resource': [
                    baseline_overrides_json
                ],
                'Condition': {
                    'StringNotEquals': {
                        f'aws:PrincipalTag/QSConfigId-{qs_configuration_id}': f'{qs_configuration_id}'
                    }
                }
            }
        ]
    }

    target_statement = {
        'Sid': 'Target',
        'Effect': 'Allow',
        'Action': 's3:GetObject',
        'Resource': baseline_overrides_json
    }

    if target_entities.upper() == 'OU':
        if len(organizational_units) == 0:
            raise ValueError('Was expecting at least one OU')

        principal_org_paths = [
            f'{principal_org_id}/*/{ou}/*' for ou in organizational_units if ou.startswith('ou-')]

        if len(principal_org_paths) == 0:
            raise ValueError('Was expecting at least one OU')

        target_statement['Principal'] = '*'
        target_statement['Condition'] = {
            'ForAnyValue:StringLike': {
                'aws:PrincipalOrgPaths': principal_org_paths
            }
        }
    elif target_entities.upper() == 'ENTIRE_ORG':
        target_statement['Principal'] = '*'
        target_statement['Condition'] = {
            'StringEquals': {
                'aws:PrincipalOrgID': [
                    f'{principal_org_id}'
                ]
            }
        }
    elif target_entities.upper() == 'LOCAL':
        target_statement['Principal'] = {"AWS": account_id}
    else:
        raise ValueError(
            'Got an unexpected value for target entities; was expecting ENTIRE_ORG, LOCAL, or OU')

    bucket_policy['Statement'].append(target_statement)

    s3_client.put_bucket_policy(
        Bucket=bucket_name,
        Policy=json.dumps(bucket_policy)
    )
    print('Bucket policy applied \n')


def put_bucket_logging(bucket_name, access_log_bucket_name):
    print('Enabling logging for the bucket... \n')
    s3_client.put_bucket_logging(
        Bucket=bucket_name,
        BucketLoggingStatus={
            'LoggingEnabled': {
                'TargetBucket': access_log_bucket_name,
                'TargetPrefix': ''
            }
        }
    )
    print('Logging enabled for the bucket \n')


def get_patch_baselines(patch_baseline_ids, request_type) -> dict:
    print('Retrieving patch baselines... \n')
    patch_baselines = []
    non_existent_baseline_ids = []

    if request_type in (CREATE, UPDATE):
        try:
            for baseline_id in patch_baseline_ids:
                baseline = ssm_client.get_patch_baseline(
                    BaselineId=baseline_id
                )
                patch_baselines.append(baseline)

            print('Patch baselines retrieved \n')
            return {
                'PatchBaselines': json.dumps(patch_baselines, default=str),
                'NonExistentBaselineIds': non_existent_baseline_ids
            }
        except ssm_client.exceptions.DoesNotExistException as err:
            print(f'Baseline id {baseline_id} does not exist')
            print(err, '\n')
            raise err

    elif request_type == REMEDIATE:  # Different behavior for Remediate by design
        for baseline_id in patch_baseline_ids:
            try:
                baseline = ssm_client.get_patch_baseline(
                    BaselineId=baseline_id
                )
                patch_baselines.append(baseline)
            except ssm_client.exceptions.DoesNotExistException:
                non_existent_baseline_ids.append(baseline_id)

        print('Patch baselines retrieved \n')
        return {
            'PatchBaselines': json.dumps(patch_baselines, default=str),
            'NonExistentBaselineIds': non_existent_baseline_ids
        }


def place_baselines_into_bucket(bucket_name, baselines):
    print('Loading the baselines... \n')
    s3_client.put_object(
        Body=baselines['PatchBaselines'],
        Bucket=bucket_name,
        Key='baseline_overrides.json',
    )
    print('Baselines loaded \n')

    if baselines['NonExistentBaselineIds']:
        print('The following baseline ids could not be found:',
              baselines['NonExistentBaselineIds'], '\n')
        raise ValueError(
            f'The following baseline ids could not be found: {baselines["NonExistentBaselineIds"]}')


def permanently_delete_all_objects(bucket_name):
    print('Deleting all objects in the bucket permanently... \n')
    bucket = s3_resource.Bucket(bucket_name)
    bucket.object_versions.all().delete()
    time.sleep(2)
    print('Bucket has been emptied \n')


def delete_bucket(bucket_name):
    print('Deleting the bucket... \n')
    s3_client.delete_bucket(
        Bucket=bucket_name
    )
    waiter = s3_client.get_waiter('bucket_not_exists')
    waiter.wait(
        Bucket=bucket_name
    )
    print('Bucket deleted successfully \n')


def empty_and_delete_bucket(bucket_name):
    try:
        s3_client.head_bucket(
            Bucket=bucket_name
        )
        permanently_delete_all_objects(bucket_name)
        delete_bucket(bucket_name)
    except Exception as err:
        # Bucket does not exist or is not owned by the account
        if err.response['Error']['Code'] == '404':
            return
        else:
            raise err


def send(event, context, responseStatus, responseData=None, physicalResourceId=None, noEcho=False, reason=None):
    request_type = event.get('RequestType')
    if not request_type in (CREATE, UPDATE, DELETE):
        return

    print('Preparing response to CloudFormation... \n')

    responseUrl = event['ResponseURL']
    responseBody = {
        'Status': responseStatus,
        'Reason': reason or f'See the details in CloudWatch Log Stream: {context.log_stream_name}',
        'PhysicalResourceId': physicalResourceId or context.log_stream_name,
        'StackId': event['StackId'],
        'RequestId': event['RequestId'],
        'LogicalResourceId': event['LogicalResourceId'],
        'NoEcho': noEcho,
        'Data': responseData
    }

    print('Response body:', responseBody, '\n')
    json_responseBody = json.dumps(responseBody)

    headers = {
        'content-type': '',
        'content-length': str(len(json_responseBody))
    }

    try:
        print('Sending response to CloudFormation via http request... \n')
        response = http.request(
            'PUT', responseUrl, headers=headers, body=json_responseBody, retries=5)
        print('Status code:', response.status, '\n')

    # If this actually happens, the stack could get stuck for an hour
    # waiting for a response from this custom resource.
    # There is a manual way to send a response using curl
    except Exception as err:
        print('Send failed executing http.request:')
        print(err, '\n')
        raise err


def lambda_handler(event, context):
    request_type = event.get('RequestType')

    # In case of Remediate, ResourceProperties only has BucketName and PatchBaselineIds
    resource_properties = event['ResourceProperties']

    bucket_name = resource_properties['BucketName']
    patch_baseline_ids = [baseline.get('value') for baseline in json.loads(resource_properties['PatchBaselines']).values()]
    access_log_bucket_name = resource_properties.get('AccessLogBucketName')

    print('Event:', event, '\n')

    try:
        if request_type == CREATE:
            create_bucket(bucket_name)
            put_bucket_versioning(bucket_name)
            put_bucket_encryption(bucket_name)
            put_public_access_block(bucket_name)
            put_bucket_lifecycle_configuration(bucket_name)
            put_bucket_policy(bucket_name, resource_properties)
            put_bucket_logging(bucket_name, access_log_bucket_name)
            place_baselines_into_bucket(
                bucket_name, get_patch_baselines(patch_baseline_ids, request_type))
            send(event, context, SUCCESS, physicalResourceId=bucket_name)

        elif request_type == UPDATE:
            # We are making an assumption that Update event will never cause creation of another bucket.
            # Bucket name is dynamically constructed using AccountId and QSConfigId
            put_bucket_policy(bucket_name, resource_properties)
            place_baselines_into_bucket(
                bucket_name, get_patch_baselines(patch_baseline_ids, request_type))
            send(event, context, SUCCESS, physicalResourceId=bucket_name)

        elif request_type == DELETE:
            empty_and_delete_bucket(bucket_name)
            send(event, context, SUCCESS, physicalResourceId=bucket_name)

        elif request_type == REMEDIATE:
            print('Starting remediation... \n')
            place_baselines_into_bucket(
                bucket_name, get_patch_baselines(patch_baseline_ids, request_type))
            print('Remediation completed \n')

        else:
            print('Unexpected request type received:', request_type)
            raise ValueError(
                'A valid RequestType is Create, Update, Delete, or Remediate')

        return SUCCESS
    except Exception as err:
        print(err, '\n')
        print('You can review the log for the Lambda function for details \n')
        send(event, context, FAILED, reason=str(err), physicalResourceId=bucket_name)
        raise err  # To send signal to Automation Document of failure
