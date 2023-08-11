import boto3
import json
from sqs_url import QUEUE_URL
tot_mssg = 0
# Create SQS client
sqs = boto3.client('sqs')

with open('fast_data.json', 'r') as f:
    data = json.loads(f.read())

for i in data:
    msg_body = json.dumps(i)
    response = sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=msg_body,
        DelaySeconds=2,
        MessageAttributes={
            'JobType': {
                'DataType': 'String',
                'StringValue': 'NewDonor'
            },
            'Producer': {
                'DataType': 'String',
                'StringValue': 'Fast'
            }
        }
    )
    tot_mssg += 1
    print(f'======= Meesage {tot_mssg} =======')
    print('Added a message with 1 second delay - FAST')
    print(response)
print(f'\nTotal messages added: {tot_mssg}')
