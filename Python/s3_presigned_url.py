import boto3
import json
import argparse
from botocore.exceptions import ClientError


# Create a presigned URL for an object in S3 that expires in a week:
def create_presigned_url(bucket_name, object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a presigned URL for an object in S3 that expires in a week')
    parser.add_argument('--bucket', help='The name of the bucket')
    parser.add_argument('--object', help='The name of the object')
    args = parser.parse_args()
    url = create_presigned_url(args.bucket, args.object)
    if url is not None:
        print('The presigned URL is {}'.format(url))