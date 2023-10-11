import json
import base64
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

output = []

def lambda_handler(event, context):
    
    sample_records = 1  # Number of records to show in logs
    total_price = 0            # Total sum of prices in all records
    status = 'Ok'              # Status of record processing
    
    count_records = len(event['records'])
    logger.info("Count records: {}".format(count_records))
    
    for record in event['records']:
        try:
            payload = base64.b64decode(record['data']).decode('utf-8')
            json_value = json.loads(payload)
            if sample_records != 0: logger.info("Original data: {}".format(json_value))
            total_price += json_value["price"]
            
        except:
            logger.error("Error in this record: {}".format(record))
            status = 'ProcessingFailed'
            continue
        
        else:
            # Change format date to ISO 8601
            new_date_sold_s = date_isoformat(json_value["dateSoldSince"])
            new_date_sold_u = date_isoformat(json_value["dateSoldUntil"])
            
            json_value["dateSoldSince"] = new_date_sold_s
            json_value["dateSoldUntil"] = new_date_sold_u
            
            new_payload = base64.b64encode(str(json_value).encode('utf-8'))
            
            if sample_records != 0:
                logger.info("New data: {}".format(json_value))
                sample_records -= 1
                    
        output_record = {
            'recordId': record['recordId'],
            'result': status,
            'data': new_payload
        }
        output.append(output_record)

    logger.info("Total price: {}".format(total_price))
    return {'records': output}

   
def date_isoformat(date_str):
    """
    Change format from: 'Wed Aug 26 2020 00:00:00 GMT+0000 (Some region)'
    to '2020-08-26T00:00:00.000Z'
    """
    date_to_convert = date_str.split(" (")[0]
    date_to_convert = datetime.strptime(date_to_convert, "%a %b %d %Y %H:%M:%S %Z%z")
    date_to_convert = date_to_convert.utcnow().isoformat()
    return date_to_convert