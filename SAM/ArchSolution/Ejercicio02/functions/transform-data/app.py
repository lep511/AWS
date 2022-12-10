# clickstream/!{partitionKeyFromLambda:tickerSymbol}/!{partitionKeyFromLambda:year}/!{partitionKeyFromLambda:month}/
import json
import base64
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

output = []

def lambda_handler(event, context):
    
    sample_record_to_logs = 3  # Number of records to show in logs
    total_price = 0            # Total sum of prices in all records
    status = 'Ok'              # Status of record processing
    
    count_records = len(event['records'])
    logger.info("Count records: {}".format(count_records))
    
    for record in event['records']:
        try:
            payload = base64.b64decode(record['data']).decode('utf-8')
            json_value = json.loads(payload)
            if sample_record_to_logs != 0:
                logger.info("Event data: {}".format(json_value))
                sample_record_to_logs -= 1
        
        except Exception as e:
            logger.error("Error decoding payload: {}".format(e))
            status = 'ProcessingFailed'
            continue
        
        else:
            # Create output Firehose record and add modified payload and record ID to it.
            firehose_record_output = {}
            
            try:
                total_price += json_value["PRICE"]
            
            except:
                logger.error("Error in this record: {}".format(e))
                status = "ProcessingFailed"    

        output_record = {
            'recordId': record['recordId'],
            'result': status,
            'data': record['data']
        }
        output.append(output_record)

    logger.info("Total price: {}".format(total_price))
    return {'records': output}