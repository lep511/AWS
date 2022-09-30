import json
print('Loading function')

def lambda_handler(event, context):
    # print('Received event: ' + json.dumps(event, indent=2))
    message = event['Records'][0]['Sns']['Message']
    print('[Service] Account Service received message: ' + message)

    return 'success'