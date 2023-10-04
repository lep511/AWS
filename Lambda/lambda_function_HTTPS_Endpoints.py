import json
import http.client

conn = http.client.HTTPSConnection("api.iplocation.net")

def lambda_handler(event, context):
    print(event)
    
    webhookPayload = json.loads(event["body"])
    webhookSignature = event["headers"].get("signature-header")
    print(webhookSignature)
    
    payload = ''
    headers = {}
    ip_request = event["headers"]["x-forwarded-for"]
    
    conn.request("POST", f"/?ip={ip_request}", payload, headers)
    res = conn.getresponse()
    data = res.read()
    data_decode = json.loads(data.decode("utf-8"))
    location = data_decode["country_name"]
    
    return {
        'statusCode': 200,
        'body': json.dumps(f'Hello from Lambda in {location}')
    }
