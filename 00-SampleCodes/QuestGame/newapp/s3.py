import boto3
from flask import Flask, redirect, url_for, request, flash, send_file


def s3_client():
    """
    Function: Initialize S3 client
    :returns: returns client
    """
    client = boto3.client( 's3' )
    return client

def s3_resource():
    """
        Function: Initialize S3 client
        :returns: returns resource
        """
    client_resource = boto3.resource( 's3' )
    return client_resource

def list_s3_buckets():
    """
        Function: list_s3_buckets
         Purpose: Get the list of s3 buckets
        :returns: s3 buckets in your aws account
    """
    client = s3_client()
    buckets_response = client.list_buckets()

    # check buckets list returned successfully
    if buckets_response['ResponseMetadata']['HTTPStatusCode'] == 200:
        for s3_buckets in buckets_response['Buckets']:
            print( f" *** Bucket Name: {s3_buckets['Name']} - Created on {s3_buckets['CreationDate']} \n" )
    else:
        print( f" *** Failed while trying to get buckets list from your account" )


def s3_upload_files(inp_file_name, s3_bucket_name, inp_file_key, content_type):
    """
           Function: upload file to bucket
           :returns: s3 buckets in your aws account
       """
    client = s3_client()
    upload_file_response = client.upload_fileobj(
        inp_file_name,
        s3_bucket_name,
        inp_file_key,
    )
    print( f" ** Response - {upload_file_response}" )


def list_s3_objects(s3_bucket_name):
    client = s3_client()
    summary = client.list_objects( Bucket=s3_bucket_name )
    summary = summary.get( 'Contents' )
    # # print(summary)
    return summary


def delete_objects(s3_bucket_name, key):
    client = s3_client()
    delete_response = client.delete_object( Bucket=s3_bucket_name, Key=key )
    # print( f" ** Response - {delete_response}" )
    return delete_response

def download_objects(s3_bucket_name, key):
    s3 = s3_resource()
    print(key)
    output = f"{key}"
    s3.Bucket(s3_bucket_name).download_file(key, output)
    return output