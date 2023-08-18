import boto3
import json


def lambda_handler(event, context):
    print(event)
    all_unencrypted_objects = []
    for item in event['Items']:
        # Get the bucket name and object key from the event
        bucket_name = "bucket_name"
        object_key = item['Key']
        
        # Check if the object is encrypted
        chek_encryption = check_server_side_encryption(bucket_name, object_key)
        
        if not chek_encryption:
            all_unencrypted_objects.append(bucket_name + '/' + object_key)            
    
    return {
        'statusCode': 200,
        'body': json.dumps(all_unencrypted_objects)
    }


def check_server_side_encryption(bucket_name, object_key):
    s3 = boto3.client('s3')
    try:
        response = s3.head_object(Bucket=bucket_name, Key=object_key)
        server_side_encryption = response.get('ServerSideEncryption')
        
        if server_side_encryption:
            print(f"The object '{object_key}' in bucket '{bucket_name}' is encrypted with '{server_side_encryption}'.")
            return True
        else:
            print(f"The object '{object_key}' in bucket '{bucket_name}' is not encrypted.")
            return False
    
    except Exception as e:
        print(f"Error checking server-side encryption: {str(e)}")
        return False