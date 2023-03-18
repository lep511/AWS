import boto3

client = boto3.client('s3', region_name='us-west-2')
paginator = client.get_paginator('list_objects')
page_iterator = paginator.paginate(Bucket='my-bucket')
filtered_iterator = page_iterator.search("Contents[?Size > `100`][]")
for key_data in filtered_iterator:
    print(key_data)
