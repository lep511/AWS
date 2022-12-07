# clickstream/!{partitionKeyFromLambda:tickerSymbol}/!{partitionKeyFromLambda:year}/!{partitionKeyFromLambda:month}/

import json
import boto3
import base64
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

output = []

def lambda_handler(event, context):
    count_records = len(event['records'])
    logger.info("Count records: {}".format(count_records))
    
    for record in event['records']:
        try:
            payload = base64.b64decode(record['data']).decode('utf-8')
            json_value = json.loads(payload)
        
        except Exception as e:
            logger.error("Error decoding payload: {}".format(e))
            status = 'ProcessingFailed'
            continue
        
        else:
            # Create output Firehose record and add modified payload and record ID to it.
            firehose_record_output = {}
            datef = json_value['EVENT_TIME']
            datef = datef.replace(" ", "")
            event_timestamp = datetime.strptime(datef, '%Y-%m-%d%H:%M:%S')
            partition_keys = {"tickerSymbol":  json_value['TICKER_SYMBOL'],
                            "year": event_timestamp.strftime('%Y'),
                            "month": event_timestamp.strftime('%m'),
                            "date": event_timestamp.strftime('%d'),
                            "hour": event_timestamp.strftime('%H'),
                            "minute": event_timestamp.strftime('%M')
                            }
            # row_w_newline = payload + "\n"
            # row_w_newline = base64.b64encode(row_w_newline.encode('utf-8'))
            status = 'Ok'

        output_record = {
            'recordId': record['recordId'],
            'result': status,
            'data': record['data'],
            'metadata': {'partitionKeys': partition_keys}
        }
        output.append(output_record)

    return {'records': output}