import boto3, logging

# AWS Lambda Function Logging in Python - More info: https://docs.aws.amazon.com/lambda/latest/dg/python-logging.html
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Boto3 - Rekognition Client
# More Info: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rekognition.html
rekognition_client = boto3.client('rekognition')


def lambda_handler(event, context):
    logger.info(event)
    response = rekognition_client.detect_moderation_labels(
        Image={"S3Object": {"Bucket": event['bucket'], "Name": event['key']}})
    logger.info(response)
    moderation_labels = response['ModerationLabels'] if 'ModerationLabels' in response else None
    if not moderation_labels:
        return {'safe_content': True}
    else:
        return {'safe_content': False}
