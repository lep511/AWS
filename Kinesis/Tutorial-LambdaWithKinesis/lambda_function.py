import json
import base64

print('Loading function')

def lambda_handler(event, context):
    #print(json.dumps(event, indent=2))
    for record in event['Records']:
        # Kinesis data is base64 encoded so decode here
        payload = base64.b64decode(record['kinesis']['data'])
        print('Decoded payload:', payload)
