import json
import base64

output = []

def lambda_handler(event, context):

    print(event)
    for record in event['records']:
        payload = base64.b64decode(record['data']).decode('utf-8')
        data_json = json.loads(payload)

        output_record = {
            'recordId': record['recordId'],
            'data': data_json
        }
        output.append(output_record)
    return {'records': output}