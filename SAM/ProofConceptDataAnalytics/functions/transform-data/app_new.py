import json
import boto3
import base64
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

output = []

def lambda_handler(event, context):
    total_price = 0
    count_records = len(event['records'])
    logger.info("Count records: {}".format(count_records))
    
    for record in event['records']:
        status = "Ok"
        payload = base64.b64decode(record['data']).decode('utf-8')
        data_json = json.loads(payload)
        try:
            total_price += data_json["price"]
        except:
            try:
                total_price += data_json["PRICE"]
            except:
                logger.error("Error in this record: {}".format(record))
                status = "ProcessingFailed"
        # row_w_newline = base64.b64encode(row_w_newline.encode('utf-8'))
        output_record = {
            'recordId': record['recordId'],
            'result': 'Ok',
            'data': record['data']
        }
        output.append(output_record)
            
    logger.info("Event data: {}".format(data_json))
    logger.info("Total price: {}".format(total_price))
    return {'records': output}