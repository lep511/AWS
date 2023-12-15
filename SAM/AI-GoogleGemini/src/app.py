import google.generativeai as genai
import boto3
import json
from PIL import Image
from botocore.exceptions import ClientError
import urllib.parse
import re
import os

API_KEY = os.environ['API_KEY']
PROMPT = os.environ['PROMPT']
TABLE_NAME = os.environ['TABLE_NAME']

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro-vision')

def lambda_handler(event, context):
    print(event)
    # Extract bucket name and key from the S3 event
    bucket = event['bucket']['name']
    key = event['object']['key']
        
    if check_extension(key):
        s_code, msg_body = generate_code(bucket, key)
    else:
        s_code = 400
        msg_body = f"No format type allowed: {key}"
    
    return {
        'statusCode': s_code,
        'body': json.dumps(msg_body)
    }


def check_extension(key):
    """
    Description: Check file extension
    
    Args:
        key (string): Key file name
    
    Returns:
        bool: True or False if extension is allowed
    """
    
    allow_format = ['.jpg', '.jpeg', '.png', '.webp', '.heif', '.heic']
    ext_file = os.path.splitext(key)[1]
    
    if ext_file in allow_format:
        return True
    else:
        return False


def generate_code(bucket, key):
    """
    Description: Generate BIC code from image
    
    Args:
        bucket (string): Bucket name
        key (string): Key name
    
    Returns:
        int: Status Code
        string: Message Body
    """
    
    s3_client = boto3.client('s3')
    file_temp = '/tmp/{}'.format(os.path.basename(key))
    
    # Download image from S3 to /tmp
    try:
        s3_client.download_file(
            Bucket=bucket,
            Key=key,
            Filename=file_temp
        )
        img = Image.open(file_temp)
    
    except Exception as e:
        print(f"[ERROR] {e}")
        return 500, str(e)
    
    # Generate content with Google Gemini
    try:
        response = model.generate_content([PROMPT, img])
        r_text = response.text
    
    except Exception as e:
        print(f"[ERROR] {e}")
        return 500, str(e)
    
    else:
        format_text = r_text.upper().replace(' ', '')
        extract_text = re.findall('[A-Z]{4}\d{7}', format_text)
        
        if not extract_text:
            print(f"[ERROR] No code found. {r_text}")
            return 400, "No code found."
        
        code = extract_text[0]
        
        try:
            pk = code[4:10]
            sk = code[0:4] + "#" + code[4:10] + "#" + code[-1]
            print(f"[INFO] PK: {pk}, SK: {sk}")
        
        except Exception as e:
            print(f"[ERROR] {e}")
            return 500, str(e)
        
        else:
            # Write data to DynamoDB Table
            s_code, msg_body = write_data(pk, sk, r_text)
            return s_code, msg_body

               
def write_data(pk, sk, data):
    """
    Description: Write BIC code to DynamoDB Table

    Args:
        pk (string): Primary Key
        sk (string): Sort Key

    Returns:
        int: Status Code
        string: Message Body
    """
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)

    item = {
        'PK': pk,
        'SK': sk,
        'data': data
    }
    
    try:
        table.put_item(Item=item)
    
    except ClientError as e:
        print(f"[ERROR] {e}")
        return 500, str(e)
    
    else:
        return 200, "Success data saved."
