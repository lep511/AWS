import json
import boto3
import base64
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

output = []

def lambda_handler(event, context):
    json_event = json.dumps(event)
    print("[INFO] event: " + json_event)
    
    count_records = len(event['records'])
    logger.info("Count records: {}".format(count_records))
    
    for record in event['records']:
        try:
            payload = base64.b64decode(record['data']).decode('utf-8')
        except Exception as e:
            logger.error("Error decoding payload: {}".format(e))
            continue
        else:
            row_w_newline = payload + "\n"
            row_w_newline = base64.b64encode(row_w_newline.encode('utf-8'))

            output_record = {
                'recordId': record['recordId'],
                'result': 'Ok',
                'data': row_w_newline
            }
            output.append(output_record)

    return {'records': output}
