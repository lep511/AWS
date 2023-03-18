import pandas as pd
import boto3
import json
import os
from decimal import Decimal
from datetime import datetime
import time
import uuid
import shutil
import logging
import argparse
from appmigrate.process_json import generate_json
from appmigrate.main_functions import generate_json_files, send_to_dynamo

description = """
Process data from a dataframe to send it to DynamoDB.
    
This is a command-line tool for migrating data from MySQL to DynamoDB.
It allows users to specify the source and target databases, 
and map MySQL tables to DynamoDB tables.
"""
    
        
if __name__ == "__main__":
    
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description=description)
    
    # Add arguments to the parser  
    parser.add_argument("-c", "--csv", type=str, help="csv file to be processed, can be gzip file.", 
                        default=None, required=False)
    
    parser.add_argument("-s", "--shard", type=int, required=False, default=4000,
                        help="Number of records in each json file")
        
    parser.add_argument("-f", "--files", type=int, required=False, default=-1,
                        help="Number of json files to process, -1 indicates all files.")
    
    parser.add_argument("--profile", required=False, default=None,
                        help="Profile from boto3 library.")    

    parser.add_argument("--table", required=False, type=str, default=None,
                        help="DynamoDB table name.")  
    
    parser.add_argument("--region", required=False, type=str, default='us-east-1',
                        help="Region where the table is located.")  
    
    parser.add_argument("-o", "--operation",
                        choices=["all", "json", "dynamo"],
                        type=str, default="all", required=False, 
                        help="Function to be executed, by default all are executed")
    # Parse the arguments
    args = parser.parse_args()
    
    csv_file = args.csv
    size_shard = args.shard
    operation = args.operation
    files_to_process = args.files
    table_name = args.table
    profile = args.profile
    region = args.region
    logging.debug(f"Operation: {operation}")

    if operation == "all" or operation == "json":
        if not csv_file:
            raise Exception('No csv file specified.')      
        df = pd.read_csv(csv_file)
        df = df.where(pd.notnull(df), None)
        response = generate_json_files(df, size_shard)
    
    elif operation == "all" or operation == "dynamo":
        if not table_name:
            raise Exception('Table name is not specified.')
        
        send_to_dynamo(table_name=table_name, 
                       count_session=files_to_process,
                       profile=profile,
                       region=region
        ) 