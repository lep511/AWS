import subprocess
import logging
import json
import sys
import boto3
import hashlib
import os
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ds_client=boto3.client('ds')

def lambda_handler(event, context):

    """    Args:
        event (dict): Lambda dictionary of event parameters. These keys must include the following:
            - SecretId: The secret ARN or identifier
            - ClientRequestToken: The ClientRequestToken of the secret version
            - Step: The rotation step (one of createSecret, setSecret, testSecret, or finishSecret)

        context (LambdaContext): The Lambda runtime information

    Raises:
        ResourceNotFoundException: If the secret with the specified arn and stage does not exist

        ValueError: If the secret is not properly configured for rotation

        KeyError: If the event parameters do not contain the expected keys

    """
    arn = event['SecretId']
    token = event['ClientRequestToken']
    step = event['Step']

    # Setup the client
    service_client = boto3.client('secretsmanager', endpoint_url=os.environ['SECRETS_MANAGER_ENDPOINT'])
    
    # Make sure the version is staged correctly
    metadata = service_client.describe_secret(SecretId=arn)
    if not metadata['RotationEnabled']:
        logger.error("Secret %s is not enabled for rotation" % arn)
        raise ValueError("Secret %s is not enabled for rotation" % arn)
    versions = metadata['VersionIdsToStages']
    if token not in versions:
        logger.error("Secret version %s has no stage for rotation of secret %s." % (token, arn))
        raise ValueError("Secret version %s has no stage for rotation of secret %s." % (token, arn))
    if "AWSCURRENT" in versions[token]:
        logger.info("Secret version %s already set as AWSCURRENT for secret %s." % (token, arn))
        return
    elif "AWSPENDING" not in versions[token]:
        logger.error("Secret version %s not set as AWSPENDING for rotation of secret %s." % (token, arn))
        raise ValueError("Secret version %s not set as AWSPENDING for rotation of secret %s." % (token, arn))

    if step == "createSecret":
        create_secret(service_client, arn, token)

    elif step == "setSecret":
        set_secret(service_client, arn, token)

    elif step == "testSecret":
        test_secret(service_client, arn, token)

    elif step == "finishSecret":
        finish_secret(service_client, arn, token)

    else:
        raise ValueError("Invalid step parameter")


def create_secret(service_client, arn, token):
    """Create the secret

    This method first checks for the existence of a secret for the passed in token. If one does not exist, it will generate a
    new secret and put it with the passed in token.

    Args:
        service_client (client): The secrets manager service client

        arn (string): The secret ARN or other identifier

        token (string): The ClientRequestToken associated with the secret version

    Raises:
        ResourceNotFoundException: If the secret with the specified arn and stage does not exist

    """
    # Make sure the current secret exists
    existingpasswd=service_client.get_secret_value(SecretId=arn, VersionStage="AWSCURRENT")
    logger.info("createSecret: Successfully retrieved existing secret for %s." % arn)
    logger.info("createSecret: Existing SecretValueString is %s." % existingpasswd['SecretString'])

    # Now try to get the secret version, if that fails, put a new secret
    try:
        service_client.get_secret_value(SecretId=arn, VersionId=token, VersionStage="AWSPENDING")
        logger.info("createSecret: Successfully retrieved secret for %s." % arn)
    except service_client.exceptions.ResourceNotFoundException:
        # Generate a random password
        newpasswd = service_client.get_random_password(ExcludeCharacters='/@"\'\\')

        # Put the secret
        service_client.put_secret_value(SecretId=arn, ClientRequestToken=token, SecretString=newpasswd['RandomPassword'], VersionStages=['AWSPENDING'])
        #service_client.put_secret_value(SecretId=arn, ClientRequestToken=token, SecretString=existingpasswd['SecretString'], VersionStages=['AWSPENDING'])
        logger.info("createSecret: Successfully put secret for ARN %s and version %s." % (arn, token))


def set_secret(service_client, arn, token):
    """Set the secret

    This method should set the AWSPENDING secret in the service that the secret belongs to. For example, if the secret is a database
    credential, this method should take the value of the AWSPENDING secret and set the user's password to this value in the database.

    Args:
        service_client (client): The secrets manager service client

        arn (string): The secret ARN or other identifier

        token (string): The ClientRequestToken associated with the secret version

    """
    # This is where the secret should be set in the service
    # Now try to get the secret version, if that fails, throw error
    try:
        newpasswd=service_client.get_secret_value(SecretId=arn, VersionId=token, VersionStage="AWSPENDING")
        logger.info("setSecret: Successfully retrieved secret for %s." % arn)
        logger.info("setSecret: SecretValueString is %s." % newpasswd['SecretString'])
        directoryid=os.environ['directoryid']
        describe_resp=ds_client.describe_directories(DirectoryIds=[directoryid])
        directorydescriptions=describe_resp['DirectoryDescriptions'][0]
        directory_id=directorydescriptions['DirectoryId']
        name=directorydescriptions['Name']
        logger.info("The Directory ID is: " + directory_id)
        logger.info("The FQDN of the directory is: " + name)
        logger.info("Updating the password of Administrator User")
        ds_client.reset_user_password(
                DirectoryId=directory_id,
                UserName='Administrator',
                NewPassword=newpasswd['SecretString']
            )
    except service_client.exceptions.ResourceNotFoundException:
        # Generate a random password
        raise ValueError("setSecret: Could not fetch password for the stage AWSPENDING")
    
    except ClientError as err:
        logger.error(f"Exception Occured {err}")
        raise Exception
    
def test_secret(service_client, arn, token):
    """Test the secret

    This method should validate that the AWSPENDING secret works in the service that the secret belongs to. For example, if the secret
    is a database credential, this method should validate that the user can login with the password in AWSPENDING and that the user has
    all of the expected permissions against the database.

    Args:
        service_client (client): The secrets manager service client

        arn (string): The secret ARN or other identifier

        token (string): The ClientRequestToken associated with the secret version

    """
    # This is where the secret should be tested against the service
    existingpasswd=service_client.get_secret_value(SecretId=arn, VersionStage="AWSCURRENT")
    md5_hash_existing_pwd = hashlib.md5(existingpasswd['SecretString'].encode('utf-8')).hexdigest()
    newpasswd=service_client.get_secret_value(SecretId=arn, VersionStage="AWSPENDING")
    md5_hash_new_pwd = hashlib.md5(newpasswd['SecretString'].encode('utf-8')).hexdigest()
    pendingversionid = newpasswd['VersionId']
    if md5_hash_existing_pwd != md5_hash_new_pwd:
        logger.info("testsecret: Testing successful.")
    else:
        service_client.update_secret_version_stage(SecretId=arn, VersionStage="AWSPENDING", RemoveFromVersionId=pendingversionid)
        logger.error("testsecret: Testing failed. Secret was not rotated. AWSPENDING stage removed")
        raise ValueError("Secret %s was not rotated or testing failed" % arn)

def finish_secret(service_client, arn, token):
    """Finish the secret

    This method finalizes the rotation process by marking the secret version passed in as the AWSCURRENT secret.

    Args:
        service_client (client): The secrets manager service client

        arn (string): The secret ARN or other identifier

        token (string): The ClientRequestToken associated with the secret version

    Raises:
        ResourceNotFoundException: If the secret with the specified arn does not exist

    """
    # First describe the secret to get the current version
    metadata = service_client.describe_secret(SecretId=arn)
    current_version = None
    logger.info("finishSecret: Starting to finish the job")
    for version in metadata["VersionIdsToStages"]:
        if "AWSCURRENT" in metadata["VersionIdsToStages"][version]:
            if version == token:
                # The correct version is already marked as current, return
                logger.info("finishSecret: Version %s already marked as AWSCURRENT for %s" % (version, arn))
                return
            current_version = version
            break

    # Finalize by staging the secret version current
    service_client.update_secret_version_stage(SecretId=arn, VersionStage="AWSCURRENT", MoveToVersionId=token, RemoveFromVersionId=current_version)
    logger.info("finishSecret: Successfully set AWSCURRENT stage to version %s for secret %s." % (token, arn))