import json
import os
from datetime import date, datetime
from urllib import request
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    
    logger.info('Event: ---{}---'.format(event))

    try:
        webhook_url = os.environ['webhook_url']
        slack_channel = os.environ['slack_channel']
    except KeyError as e:
        error_text = "Missing environment variable: {}".format(e)
        logger.error(error_text)
        return { 
            'statusCode': 500,
            'body': json.dumps(error_text)
        }  
    
    finding = event['detail']['findings'][0]['Types'][0]
    finding_description = event['detail']['findings'][0]['Description']
    finding_time = event['detail']['findings'][0]['UpdatedAt']
    # finding_time_epoch = int(finding_time.timestamp())
    account = event['detail']['findings'][0]['AwsAccountId']
    region = event['detail']['findings'][0]['Resources'][0]['Region']
    type = event['detail']['findings'][0]['Resources'][0]['Type']
    message_id = event['detail']['findings'][0]['Resources'][0]['Id']
    last_seen = datetime.strptime(finding_time, '%Y-%m-%dT%H:%M:%S.%fZ')
    
    if 1 <= event['detail']['findings'][0]['Severity']['Normalized'] <= 39:
        severity = 'LOW'
        color = '#879596'
    elif 40 <= event['detail']['findings'][0]['Severity']['Normalized'] <= 69:
        severity = 'MEDIUM'
        color = '#ed7211'
    elif 70 <= event['detail']['findings'][0]['Severity']['Normalized'] <= 89:
        severity = 'HIGH'
        color = '#ed7211'
    elif 90 <= event['detail']['findings'][0]['Severity']['Normalized'] <= 100:
        severity = 'CRITICAL'
        color = '#ff0209'
    else:
        severity = 'INFORMATIONAL'
        color = '#007cbc'
        
    attachment = [{
        "fallback": finding + ' - https://console.aws.amazon.com/securityhub/home?region=' + region + '#/findings?search=id%3D' + message_id,
        "pretext": '*AWS SecurityHub finding in ' + region + ' for Acct: ' + account + '*',
        "title": finding,
        "title_link": 'https://console.aws.amazon.com/securityhub/home?region=' + region + '#/research',
        "text": finding_description,
        "fields": [
            {
                "title": "Severity",
                "value": severity,
                "short": True
            },
            {
                "title": "Region",
                "value": region,
                "short": True
            },
            {
                "title": "Resource Type",
                "value": type,
                "short": True
            },
            {
                "title": "Last Seen",
                "value": last_seen,
                "short": True
            }
        ],
        "mrkdwn_in": [
            "pretext"
        ],
        "color": color
    }]
    
    slack_message = {
        'channel': slack_channel,
        'text' : '',
        'attachments' : attachment,
        'username': 'SecurityHub',
        'mrkdwn': 'true',
        'icon_url': 'https://raw.githubusercontent.com/aws-samples/amazon-securityhub-to-slack/master/images/gd_logo.png'
    }
    
    response = request.urlopen(
        webhook_url, data=json.dumps(slack_message, default=json_serial).encode('utf-8')
    )
    if response.getcode() != 200:
        raise ValueError(
            'Request to slack returned an error %s, the response is:\n%s'
            % (response.getcode(), response.read())
        )
    return { 
        'statusCode': 200,
        'body': json.dumps("Message posted successfully!")
    }  


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))