import json
import boto3
import base64

output = []

def lambda_handler(event, context):

    for record in event['records']:
        payload = base64.b64decode(record['data']).decode('utf-8')

        row_w_newline = payload + "\n"
        row_w_newline = base64.b64encode(row_w_newline.encode('utf-8'))

        output_record = {
            'recordId': record['recordId'],
            'result': 'Ok',
            'data': row_w_newline
        }
        output.append(output_record)

    return {'records': output}