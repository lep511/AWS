import google.generativeai as genai
from botocore.exceptions import ClientError
from pathlib import Path
import boto3
import json
import hashlib
import os

TABLE_NAME = os.environ['TABLE_NAME']

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


def upload_if_needed(pathname: str) -> list[str]:
    path = Path(pathname)
    hash_id = hashlib.sha256(path.read_bytes()).hexdigest()
    try:
        existing_file = genai.get_file(name=hash_id)
        return [existing_file]
    except:
        pass
    upload_file = genai.upload_file(path=path, display_name=hash_id)
    return upload_file


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
    
    # Set up Gemini
    API_KEY = os.environ['API_KEY']
    genai.configure(api_key=API_KEY)
    
    # Set up the model
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 0,
        "max_output_tokens": 1024,
    }

    safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_ONLY_HIGH"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_ONLY_HIGH"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_ONLY_HIGH"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_ONLY_HIGH"
    },
    ]
    
    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                              generation_config=generation_config,
                              safety_settings=safety_settings)
    
    # Download image from S3 to /tmp
    try:
        s3_client.download_file(
            Bucket=bucket,
            Key=key,
            Filename=file_temp
        )
    
    except Exception as e:
        print(f"[ERROR] {e}")
        return 500, str(e)
    
    # Generate content with Google Gemini
    file_img_ref = upload_if_needed("idnumber.png")
    file_img_tmp = upload_if_needed(file_temp)
    
    prompt_parts = [
        "Follow these instructions to extract the container code.\n\n",
        file_img_ref,
        "\n\nExtract the complete code from this container. And response in JSON format: {\"owner_prefix\": \"BIC\", \"equipment_id\": \"U\", \"serial_num\": \"02345\", \"check_num\": \"5\"}\nRules: \n   * owner_prefix: only three words\n   * equipment_id: only one word\n   * serial_num: always six numbers\n   * check_num: always one number\n\n",
        file_img_tmp
    ]
    response = model.generate_content(prompt_parts)
    
    f_text = response.text.replace("```json", "").replace("```", "").replace("\n", "")
    json_data = json.loads(f_text)
       
    try:
        s_code, msg_body = write_data(json_data)
    
    except Exception as e:
        print(f"[ERROR] {e}")
        return 500, str(e)
    
    else:
        # Delete uploaded files except the first one
        genai.delete_file(file_img_tmp.name)
        return s_code, msg_body

               
def write_data(json_data):
    """
    Description: Write BIC code to DynamoDB Table

    Args:
        json_data (dict): BIC code data

    Returns:
        int: Status Code
        string: Message Body
    """
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)

    item = {
        'PK': json_data['owner_prefix'],
        'SK': json_data['serial_num'],
        'owner_prefix': json_data['owner_prefix'],
        'serial_num': json_data['serial_num'],
        'equipment_id': json_data['equipment_id'],
        'check_num': json_data['check_num'] 
    }
    
    try:
        table.put_item(Item=item)
    
    except ClientError as e:
        print(f"[ERROR] {e}")
        return 500, str(e)
    
    else:
        return 200, "Success data saved."
