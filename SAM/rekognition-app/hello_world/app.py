import os
import json
import boto3
import requests
import botocore.exceptions

s3_client = boto3.client("s3")
S3_BUCKET = os.getenv("BUCKET_NAME")

# 1.) Function to get a file from url
def get_file_from_url(url):
    try:
        response = requests.get(url)
        return response.content
    except requests.exceptions.RequestException as e:
        print(e)
        return False

# 2.) Function to upload image to S3
def upload_image_to_s3(bucket, key, data):
    """
    Uploads an image to S3
    """
    try:
        response = s3_client.head_object(
            Bucket=bucket, 
            Key=key
        )
        print(response)
    except:
        pass
    else:
        print("File exist")
        return {
            "status_code": 409,
            "msg_code": "File already exists."
        }
    try:
        print("Uploading image to S3")
        s3_client.put_object(Body=data, Bucket=bucket, Key=key)
        return {
            "status_code": 200,
            "msg_code": "Successfully Uploaded Img!"
        }
    except botocore.exceptions.ClientError as e:
        print("Error uploading image to S3")
        print(e)
        return {
            "status_code": 400,
            "msg_code": "Can't write to S3."
        }

def lambda_handler(event, context):
    print(event)
    url = event["queryStringParameters"]["url"]
    name = event["queryStringParameters"]["name"]

    response = get_file_from_url(url)
    
    if response:
        # pass the output of function #1 as input to function #2
        response = upload_image_to_s3(S3_BUCKET, name, get_file_from_url(url))
    else:
        response = {
            "status_code": 404,
            "msg_code": "Can't load the image."
        }
    
    return {
        'statusCode': response["status_code"],
        'body': json.dumps(response["msg_code"])
    }
