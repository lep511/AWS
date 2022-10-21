import json
import urllib.parse
import boto3

s3 = boto3.client('s3')


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['detail']['bucket']['name']
    key = urllib.parse.unquote_plus(event['detail']['object']['key'], encoding='utf-8')

    response = s3.get_object(Bucket=bucket, Key=key)
    cont_type = response['ContentType']
    print("CONTENT TYPE: " + cont_type)
    if cont_type == 'text/plain':
        text_data = response['Body'].read().decode('utf-8')
        return {
            'statusCode': 200,
            'body': text_data
        }
    else:
        return {
            'statusCode': 400,
            'body': json.dumps("No format type: text-plain")
            }