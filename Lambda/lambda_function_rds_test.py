# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import sys
import pymysql
import boto3
import botocore
import json
import random
import time
import os
from botocore.exceptions import ClientError
conn = None

# rds settings
rds_host = os.environ['RDS_HOST']
username = os.environ['RDS_USERNAME']
db_name = os.environ['RDS_DB_NAME']
password = os.environ['PASSWORD']

def openConnection():
    global conn
    global describe_secret_response_version

    # PRESS ENTER AFTER THIS COMMENT AND PASTE THE COPIED SAMPLE CODE FROM AWS SECRETS MANAGER
    
    
    #secretstring = json.loads(secret)
    #rds_host = secretstring['host']
    #username = secretstring['username']
    #password = secretstring['password']
    #db_name =  secretstring['dbname']
    

    try:
        print("Opening Connection")
        if(conn is None):
            conn = pymysql.connect(host=rds_host, user=username, passwd=password, db=db_name, connect_timeout=5)
            get_describe_secret_response = client.describe_secret(SecretId=secret_name)
            describe_secret_response_version = str(get_describe_secret_response['VersionIdsToStages'])
        elif (not conn.open):
            conn = pymysql.connect(host=rds_host, user=username, passwd=password, db=db_name, connect_timeout=5)
            get_describe_secret_response = client.describe_secret(SecretId=secret_name)
            describe_secret_response_version = str(get_describe_secret_response['VersionIdsToStages'])

    except Exception as e:
        print (e)
        print("ERROR: Unexpected error: Could not connect to MySql instance.")
        raise e


def lambda_handler(event, context):

    try:
        openConnection()
        if(conn.open):
            with conn.cursor() as cur:
                cur.execute("select * from DemoTable")
                records = cur.fetchall()
                p = []
                tbl = "<tr><td>First Name</td><td>Last Name</td></tr>"
                p.append(tbl)
                
                for row in records:
                    a = "<tr><td>%s</td>"%row[1]
                    p.append(a)
                    b = "<td>%s</td></tr>"%row[2]
                    p.append(b)
            
                lst = str(p)
                f=lst.replace("', '", "")
                g=f.replace("[", "")
                h=g.replace("]","")
                x=h.replace("'", "")
                content = "<html><head><style>table, th, td {  border: 1px solid black;}</style><title>AWS Secrets Manager workshop</title></head><body><table>%s</table></body></html>"%(x)
                
                response = {
                    "statusCode": 200,
                    "body": content+describe_secret_response_version,
                    "headers": {
                        'Content-Type': 'text/html' ,
                    }
                }
                return response
    except Exception as e:
        print(e)
        content =  "<html><head><title>AWS Secrets Manager workshop</title></head><body>Database not connected</body></html>"                
        response = {
            "statusCode": 200,
            "body": content,
            "headers": {
                'Content-Type': 'text/html' ,
                
            }
            
        }
        return response
    finally:
        print("Closing Connection")
        if(conn is not None and conn.open):
            conn.close()
    