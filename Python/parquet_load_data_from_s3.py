import io
import boto3
import pandas as pd
import pyarrow.parquet as pq

bucket_name = 'sam-app-bucket-51568'
def download_s3_parquet_file(s3, bucket, key):
    buffer = io.BytesIO()
    s3.Object(bucket, key).download_fileobj(buffer)
    return buffer

client = boto3.client('s3')
s3 = boto3.resource('s3')
objects_dict = client.list_objects_v2(Bucket=bucket_name, Prefix='retail-cart-data')
s3_keys = [item['Key'] for item in objects_dict['Contents'] if item['Key'].endswith('.parquet')]
buffers = [download_s3_parquet_file(s3, bucket_name, key) for key in s3_keys]
dfs = [pq.read_table(buffer).to_pandas() for buffer in buffers]
df = pd.concat(dfs, ignore_index=True)
