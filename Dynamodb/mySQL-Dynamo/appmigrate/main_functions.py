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
from appmigrate import directories as dr

JSON_DIR = dr.JSON_DIR
PROC_DIR = dr.PROC_DIR
ERRO_DIR = dr.ERRO_DIR

# Set up basic logging configuration
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

##########################################################################################################
# 0 - Help functions
########################################################################################################## 

def actual_num_files(direct):
    return [f for f in os.listdir(direct) if os.path.isfile(os.path.join(direct,f))]


def select_dynamo_table(table_name, profile=False, region='us-east-1'):
    
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

def send_to_dynamo(table_name, count_session=-1, profile=False, region="us-east-1"):
    
    dynamo_table = select_dynamo_table(table_name=table_name, profile=profile, region=region)
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
        
        count_session -= 1
        count_files_end -= 1
        # Exit loop if count_session is 0
        if count_session == 0:
            break
       
    
    tot_all_sec = round(time.time() - init_time)
    tot_time = convert(tot_all_sec)
    logging.info(f"Total time: {tot_time}")
    
    if len(errors) > 0:
        record_errors(errors)
    else:
        logging.info("No errors were found.")