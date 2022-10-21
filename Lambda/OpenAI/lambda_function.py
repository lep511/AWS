import json
import openai

openai.api_key = "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"

def lambda_handler(event, context):
    text_ingress = event['body']
    resp = ai_function(text_ingress)
    return {
        'statusCode': 200,
        'body': json.dumps(resp)
    }

def ai_function(text_function):
    response = openai.Completion.create(
      model="text-davinci-002",
      prompt=text_function,
      temperature=0,
      max_tokens=260,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0,
      stop=["**"]
    )
    print(response)
    text_out = response["choices"][0]["text"]
    
    return text_out
