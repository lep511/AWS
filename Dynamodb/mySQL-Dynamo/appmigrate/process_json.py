import json
from decimal import Decimal
import logging

# Set up basic logging configuration
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

def generate_json(item):
    n_errors = []
    jsfl = {
        "id": item["tconst"],
        "sk": item["nconst"],
    }
    ##### ORDERING ######
    if item["ordering"]: 
        try:
            jsfl["ordering"] = int(item["ordering"])
        except Exception as e:
            logging.error(f"[ERROR] Can't process this item: {item['ordering']}. Error message: {e}")
            n_errors.append(item)
    
    ##### CATEGORY ######
    if item["category"]: 
        try:
            jsfl["category"] = item["category"]
        except Exception as e:
            logging.error(f"[ERROR] Can't process this item: {item['category']}. Error message: {e}")
            n_errors.append(item)
    
    ##### GENRES #####
    if item["genres"]: 
        try:
            if isinstance(item["genres"], str):
                jsfl["genres"] = item["genres"].split(",")
            else:
                jsfl["genres"] = item["genres"]
            
        except Exception as e:
            logging.error(f"[ERROR] Can't process this item: {item['genres']}. Error message: {e}")
            n_errors.append(item)
            
    ##### JOB #####
    if item["job"]: 
        jsfl["job"] = item["job"]    
    
    ##### CHARACTERS #####
    if item["characters"]:
        try:
            jsfl["characters"] = item["characters"]
        except Exception as e:
            logging.error(f"[ERROR] Can't process this item: {item['characters']}. Error message: {e}")
            n_errors.append(item)
    
    ##### PRIMARY-NAME #####
    if item["primaryName"]:
        jsfl["primaryName"] = item["primaryName"]
    
    ##### WRITERS #####
    if item["writers"]: 
        try:
            if isinstance(item["writers"], str):
                jsfl["writers"] = item["writers"].split(",")
            else:
                jsfl["writers"] = item["writers"]
        
        except Exception as e:
            logging.error(f"[ERROR] Can't process this item: {item['writers']}. Error message: {e}")
            n_errors.append(item)
    
    return jsfl, n_errors