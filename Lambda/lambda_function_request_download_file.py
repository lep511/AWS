import json
import boto3
import urllib3
import urllib.request
import os

def lambda_handler(event, context):

    s3=boto3.resource('s3')
    http=urllib3.PoolManager()

    url = 'https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/index.csv'
    s3Bucket = '<bucket_name>'
    key = 'od_pricedata/ec2_prices.csv'

    urllib.request.urlopen(url)   #Provide URL
    s3.meta.client.upload_fileobj(http.request('GET', url, preload_content=False), s3Bucket, key)

    return {
        'statusCode': 200,
        'body': json.dumps('YAY!')
    }