import json
import random

with open('questions.json') as json_file:
    quest = json.load(json_file)

def lambda_handler(event, context):
    num = event.get('num')
    
    if not num:
      num_ = range(0, len(quest["questions"]))
      num = random.choice(num_)
    
    if num > len(quest["questions"]):
      return "Num question out of range"
      
    return {
        'statusCode': 200,
        'body': json.dumps(quest["questions"][num])
    }
