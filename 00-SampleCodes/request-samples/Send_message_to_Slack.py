from urllib3 import PoolManager
import json

"""
This is a simple example of how to send a message to Slack using Incoming Webhooks.
For more detailed instructions, see https://api.slack.com/incoming-webhooks
"""

# The webhook_url is the unique URL generated when you create the Incoming Webhook.
webhook_url = 'https://hooks.slack.com/services/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'
# This is the name of the channel
slack_channel = 'my-data'

attachment = [{
    "fallback": 'finding' + ' - https://console.aws.amazon.com/securityhub/home?region=' + 'region' + '#/findings?search=id%3D' + 'message_id',
    "pretext": '*AWS SecurityHub finding in ' + 'region' + ' for Acct: ' + 'account' + '*',
    "title": 'finding',
    "title_link": 'https://console.aws.amazon.com/securityhub/home?region=' + 'region' + '#/research',
    "text": 'finding_description',
    "fields": [
        {
            "title": "Severity",
            "value": 'severity',
            "short": True
        },
        {
            "title": "Region",
            "value": 'region',
            "short": True
        }
    ],
    "mrkdwn_in": [
        "pretext"
    ],
    "color": '#007cbc'
}]

slack_message = {
    'channel': slack_channel,
    'text' : '',
    'attachments' : attachment,
    'username': 'SecurityHub',
    'mrkdwn': 'true',
    'icon_url': 'https://raw.githubusercontent.com/aws-samples/amazon-securityhub-to-slack/master/images/gd_logo.png'
}

http = PoolManager()
response = http.request(
        'POST', 
        webhook_url,
        body=json.dumps(slack_message).encode('utf-8'),
        headers={
            'Content-Type': 'application/json'
        }
    )

if response.status == 200:
    print('Message posted successfully!')
else:
    print('Request to slack returned an error %s, the response is:\n%s' % (response.status, response.data))
