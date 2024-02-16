import json
import os
import http.client
import urllib.parse

def lambda_handler(event, context):
    BOT_TOKEN = os.environ.get('TOKEN')
    API_KEY = os.environ.get('G_TOKEN')
    BOT_CHAT_ID = "795876358"
    
    message = event['Records'][0]['Sns']['Message']
    guardduty_finding = json.loads(message)['detail']['findings'][0]['Description']
    
    conn = http.client.HTTPSConnection("generativelanguage.googleapis.com")
    headers = { 'Content-Type': 'application/json' }
    gconfig = {
        "temperature": 0.2,
        "topK": 32,
        "topP": 1,
        "maxOutputTokens": 512,
        "stopSequences": []
    }
    prompt = f"Explain this finding from AWS GuardDuty: {guardduty_finding}"
    
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": gconfig 
    }
    
    params = json.dumps(data)
    
    conn.request("POST", f"/v1beta/models/gemini-pro:generateContent?key={API_KEY}", params, headers)

    res = conn.getresponse()
    data = res.read()
    data = data.decode("utf-8")
    js_data = json.loads(data)
    MESSAGE = ""
    for part in js_data['candidates'][0]['content']['parts']:
        MESSAGE += part['text']
        
    response = send_message(MESSAGE, BOT_TOKEN, BOT_CHAT_ID)
    
    return {
        'statusCode': 200,
        'body': json.dumps("OK")
    }


def send_message(bot_message, token, chat_id):
    message = urllib.parse.quote(bot_message)

    conn = http.client.HTTPSConnection("api.telegram.org")

    # Prepare the request URL
    send_text = f"/bot{token}/sendMessage?chat_id={chat_id}&parse_mode=HTML&text={message}"
    # Send the GET request to the Telegram API
    conn.request("GET", send_text)
    # Get the response
    response = conn.getresponse()
    print(response.status, response.reason)

    # Close the connection
    conn.close()

    return response

