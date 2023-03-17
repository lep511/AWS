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
from process_json import generate_json

# Set up basic logging configuration
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

description = """
Process data from a dataframe to send it to DynamoDB.
    
This is a command-line tool for migrating data from MySQL to DynamoDB.
It allows users to specify the source and target databases, 
and map MySQL tables to DynamoDB tables.
"""

JSON_DIR = "json_data/"
ERRO_DIR = f"{JSON_DIR}/errors/"
PROC_DIR = f"{JSON_DIR}/process/"

##########################################################################################################
# 0 - Help functions
########################################################################################################## 

def actual_num_files(direct):
    return [f for f in os.listdir(direct) if os.path.isfile(os.path.join(direct,f))]


def select_dynamo_table(name_table, profile=False, region='us-east-1'):
    
    if profile:
        session = boto3.Session(profile_name=profile, region_name=region)
        dynamodb = session.resource('dynamodb', region_name=region)
    else:
        dynamodb = boto3.resource('dynamodb', region_name=region)

    table = dynamodb.Table(table_name)
    return table


def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    
    if hour > 1:
        return "{} hours, {} minutes and {} seconds.".format(hour, minutes, seconds)
    elif hour == 1:
        return "1 hour,{} minutes and {} seconds.".format(minutes, seconds)
    elif hour == 0 and minutes > 0:
        return "{} minutes and {} seconds.".format(minutes, seconds)
    else:
        return "{} seconds.".format(seconds)


def record_errors(errors):
    
    logging.info(f"Found {len(errors)} errors.")

    if not os.path.isdir(ERRO_DIR):
        os.mkdir(ERRO_DIR)
       
    for error in errors:
        try:
            json_object = json.dumps(error, indent=4)
        
        except Exception as e:
            logging.error(f"[ERROR] Can't convert to json this: {error}. Error message: {e}")
            json_object= error
        

        now = datetime.now()
        file_name = f"errors-{now.strftime('%d-%m-%Y-')}{str(uuid.uuid4())}.json"
    
        # Writing to sample.json
        with open(ERRO_DIR + file_name, "w") as outfile:
            outfile.write(json_object)
        
##########################################################################################################
# 1 - Generate json files
##########################################################################################################  

def generate_json_files(df, size_shard=4000):
    data = []
    n_count = 0
    reg_errors = []
    
    if len(df) % size_shard == 0:
        n_pass = int(len(df) / size_shard)
    else:
        n_pass = int(len(df) / size_shard) + 1

    if os.path.isdir(JSON_DIR):
        actual_files = actual_num_files(JSON_DIR)
        if len(actual_files) > 0:
            raise Exception('Folder contain files.')  
    else:
        os.mkdir(JSON_DIR)
        actual_files = []
        
    for p in range(1, n_pass + 1):
        
        logging.info(f"Pass {p} from {n_pass}")
        
        if (n_count + size_shard) > len(df):
            t_count = n_count
            size_shard = abs(t_count - len(df))
            logging.info(f"Total records process: {n_count + size_shard}")
        
        for i in range(size_shard):
            
            ###################################################
            ####  Send to generate_json function
            
            item_json = df.iloc[i+n_count].to_json()
            item_format = json.loads(item_json)
            
            js, errors = generate_json(item_format)
            
            data.append(js)
            if errors:
                reg_errors.append(errors)
        
        file_json = JSON_DIR + "/data-" + str(p) + ".json"
        
        with open(file_json, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        data = []
        n_count += size_shard
    
    logging.info(f"Process {p} files.")
    
    if len(reg_errors) > 0:
        record_errors(reg_errors)
    

##########################################################################################################
# 2 - Send to Dynamo
##########################################################################################################  

def send_to_dynamo(dynamo_table, count_session=-1):
    
    # Get a list of all JSON files in the specified directory
    all_files = actual_num_files(JSON_DIR)
    process_files = []
    errors = []
    # Initialize count_files_end to the total number of files
    count_files_end = len(all_files)

    if count_session > len(all_files) or count_session < 0:
        count_session = len(all_files)
        int_count_session = count_session
    
    elif count_session == 0:
        raise Exception('count_session cannot be 0')
    
    else:
        int_count_session = count_session
    
    # Record start time for processing
    init_time = time.time()
    
    for i, file in enumerate(all_files, start=1):
        
        # Calculate remaining files in session and log progress
        rest_cs = abs(int_count_session - count_session) + 1
        
        logging.info(f"[INFO] ===================== File: {file} ==============================")
        logging.info(f"[INFO] Processing file {i}/{count_files_end}: {file} - {rest_cs}/{int_count_session} session process files.")
        
        # Record start time for processing each file
        start_time = time.time()
        
        # Load JSON data from file
        with open(JSON_DIR + file) as json_data:
            parsed = json.load(json_data, parse_float=Decimal)
        
        # Write records to DynamoDB table
        with dynamo_table.batch_writer() as writer:
            for item in parsed:
                try:
                    writer.put_item(Item=item)
                except Exception as e:
                    # Log error and add item to error list
                    logging.error(f"[ERROR] In the item: {item}. Error message: {e}")
                    errors.append(item)
        
        # Move file to processed directory
        if not os.path.isdir(PROC_DIR):
            os.mkdir(PROC_DIR)
        shutil.move(JSON_DIR + file, PROC_DIR + file)
        
        # Calculate processing time and estimated time remaining
        tot_sec = round(time.time() - start_time)
        calc_t = tot_sec * (count_session - 1)
        
        remain_sec = convert(calc_t)
        logging.info(f"[INFO] Time consumed for file: {tot_sec} seconds. Estimated time remaining: {remain_sec}")
        
        # Exit loop if count_session is 0
        if count_session == 0:
            break
        else:
            count_session -= 1
            count_files_end -= 1
    
    tot_all_sec = round(time.time() - init_time)
    tot_time = convert(tot_all_sec)
    logging.info(f"Total time: {tot_time}")
    
    if len(errors) > 0:
        record_errors(errors)
    else:
        logging.info("No errors were found.")

##########################################################################################################
# Main
##########################################################################################################       
        
if __name__ == "__main__":
    
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description=description)
    
    # Add arguments to the parser  
    parser.add_argument("-d", "--dataframe", type=str, help="Dataframe name to be processed", 
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
    
    dataframe_name = args.dataframe
    size_shard = args.shard
    operation = args.operation
    files_to_process = args.files
    table_name = args.table
    profile = args.profile
    region = args.region
    logging.debug(f"Operation: {operation}")

    if operation == "all" or operation == "json":
        if not dataframe_name:
            raise Exception('No dataframe was specified.')      
        df = pd.read_csv(dataframe_name)
        df = df.where(pd.notnull(df), None)
        response = generate_json_files(df, size_shard)
    
    elif operation == "all" or operation == "dynamo":
        if not table_name:
            raise Exception('Table name is not specified.')
        table = select_dynamo_table(name_table=table_name, profile=profile, region=region)
        send_to_dynamo(dynamo_table=table, count_session=files_to_process) 