import pandas as pd
import boto3
import json
import os
from decimal import Decimal
from datetime import datetime
import time
import shutil
import logging
import argparse
from appmigrate.process_json import generate_json

# Set up basic logging configuration
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

JSON_DIR = "json_data/"
ERRO_DIR = f"{JSON_DIR}/errors/"
PROC_DIR = f"{JSON_DIR}/process/"

def actual_num_files(direct):
    return [f for f in os.listdir(direct) if os.path.isfile(os.path.join(direct,f))]


def record_errors(errors):
    
    logging.info(f"Found {len(errors)} errors.")

    if not os.path.isdir(ERRO_DIR):
        os.mkdir(ERRO_DIR)
    
    json_object = json.dumps(errors, indent=4)
    now = datetime.now()
    file_name = "errors-" + now.strftime("%d-%m-%Y-") + now.strftime("%H%M%S") + ".json"
    
    # Writing to sample.json
    with open(ERRO_DIR + file_name, "w") as outfile:
        outfile.write(json_object)
  

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
            js, errors = generate_json(df.iloc[i+n_count])
            data.append(js)
            if errors:
                reg_errors.append(errors)
        
        file_json = JSON_DIR + "/data-" + str(p) + ".json"
        
        with open(file_json, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        data = []
        n_count += size_shard
    
    logging.info(f"Process {actual_files} files.")
    
    if len(reg_errors) > 0:
        record_errors(reg_errors)
  

def send_to_dynamo(count_session=-1):
    
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

    
    for i, file in enumerate(all_files, start=1):
        
        # Calculate remaining files in session and log progress
        rest_cs = abs(int_count_session - count_session) + 1
        logging.info(f"Processing file {i}/{count_files_end}: {file} - {rest_cs}/{int_count_session} session process files.")
        
        # Record start time for processing
        start_time = time.time()
        
        # Load JSON data from file
        with open(JSON_DIR + file) as json_data:
            parsed = json.load(json_data, parse_float=Decimal)
        
        # Write records to DynamoDB table
        with table.batch_writer() as writer:
            for item in parsed:
                try:
                    writer.put_item(Item=item)
                except Exception as e:
                    # Log error and add item to error list
                    logging.error(f"[ERROR] In the item: {item}. Error message: {e}")
                    errors.append(item)
        
        # Calculate processing time and estimated time remaining
        tot_sec = round(time.time() - start_time)
        reamin_sec = convert(tot_sec * (count_session - 1))
        logging.info(f"Processing time for file {i}/{count_files_end}: {tot_sec} seconds. Estimated time remaining: {remain_sec} seconds.")
        
        # Move file to processed directory
        if not os.path.isdir(PROC_DIR):
            os.mkdir(PROC_DIR)
        shutil.move(JSON_DIR + file, PROC_DIR + file)
        
        # Exit loop if count_session is 0
        if count_session == 0:
            break
        else:
            count_session -= 1
            count_files_end -= 1
    
    if len(errors) > 0:
        record_errors(errors)
    else:
        logging.info("No errors were found.")
        
        
if __name__ == "__main__":
    
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="Process data from a dataframe to send it to DynamoDB.")
    
    # Add arguments to the parser  
    parser.add_argument("-d", "--dataframe", type=str, help="Dataframe name to be processed", required=True)
    
    parser.add_argument("-s", "--size_shard", type=int, required=False, default=4000,
                        help="Number of records in each json file")
    
    parser.add_argument("-f", "--files_to_process", type=int, required=False, default=-1,
                        help="Number of json files to process, -1 indicates all files.")

    parser.add_argument("-o", "--operation",
                        choices=["all", "json", "dynamo"],
                        type=str, default="all", required=False, 
                        help="Function to be executed, by default all are executed")
    # Parse the arguments
    args = parser.parse_args()

    # Print a message with the name argument
    print(f"Hello, {args.dataframe}!")


    