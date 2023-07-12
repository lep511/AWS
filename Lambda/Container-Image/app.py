import aws_encryption_sdk
from aws_encryption_sdk import CommitmentPolicy
import sys

print(aws_encryption_sdk.__version__)

def handler(event, context):
    return 'Hello from AWS Lambda using Python' + sys.version + '!'        
