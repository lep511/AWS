import json
from decimal import Decimal

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
        except:
            n_errors.append(item)
    
    ##### CATEGORY ######
    if item["category"]: 
        jsfl["category"] = item["category"]
    
    ##### GENRES #####
    if item["genres"]: 
        try:
            jsfl["genres"] = item["genres"].split(",")
        except:
            n_errors.append(item)
            
    ##### JOB #####
    if item["job"]: 
        jsfl["job"] = item["job"]    
    
    ##### CHARACTERS #####
    if item["characters"]:
        try:
            jsfl["characters"] = json.loads(item["characters"])
        except:
            n_errors.append(item)
    
    ##### PRIMARY-NAME #####
    if item["primaryName"]:
        jsfl["primaryName"] = item["primaryName"]
    
    ##### WRITERS #####
    if item["writers"]: 
        jsfl["writers"] = item["writers"].split(",")
    
    return jsfl, n_errors