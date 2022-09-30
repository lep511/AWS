import boto3, json, logging

# AWS Lambda Function Logging in Python - More info: https://docs.aws.amazon.com/lambda/latest/dg/python-logging.html
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Boto3 - s3 Client
# More Info: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rekognition.html
s3 = boto3.client('s3')
# More Info: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/stepfunctions.html?highlight=stepfunctions
step = boto3.client('stepfunctions')


def lambda_handler(event, context):
    logger.info(event)
    for record in event['Records']:
        # Get the bucket name and key for the new file
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        # Get, read, and split the file into lines
        obj = s3.get_object(Bucket=bucket, Key=key)
        response_metadata = s3.head_object(Bucket=bucket, Key=key)
        logger.info('---- Metadata from S3 ----')
        logger.info(response_metadata)

        if response_metadata.get('Metadata') and response_metadata.get('Metadata').get('message'):
            input_step = {
                "s3_info": {
                    'bucket': bucket,
                    'key': key
                },
                "message": {
                    'content': response_metadata['Metadata']['message']
                }

            }
            logger.info('Will start Step function with Input: ' + json.dumps(input_step))
            step.start_execution(
                stateMachineArn='<Step Functions ARN>',
                # name='string',
                input=json.dumps(input_step)
            )
        else:
            logger.info("No metadata found in S3 image")
