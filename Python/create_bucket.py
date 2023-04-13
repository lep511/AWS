import boto3
import uuid

client = boto3.client('s3')
BUCKET_NAME = 'my-bucket-' + str(uuid.uuid4())

# Create a bucket
response = client.create_bucket(
    ACL='private',
    Bucket=BUCKET_NAME,
)

print(response)

