import json
import base64
import urllib.parse

def lambda_handler(event, context):
    body = event['body']
    json_data = base64_to_json(body)

    print(json_data)
    print(type(json_data))
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!'),
    }

def base64_to_json(encoded_string):
    try:
        decoded_bytes = base64.b64decode(encoded_string)
        decoded_string = decoded_bytes.decode('utf-8')
        result = urllib.parse.unquote(decoded_string)
        result = result.replace("payload=", "")
        result = result.replace("\t", "")
        result = result.replace("\n", "")
        result = result.replace("\t", "")
        result = result.replace("\b", "")
        result = result.replace("\f", "")
        result = result.replace("\/", "/")
        result = json.loads(result)
        return result
    
    except Exception as e:
        print("Error converting base64 to JSON:", e)
        return None