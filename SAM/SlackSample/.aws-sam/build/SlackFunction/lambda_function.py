# Link: https://api.slack.com/tools/block-kit-builder
import json
import sys
import os
from slack_sdk.webhook import WebhookClient

# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)


def lambda_handler(event, context):
    url = os.environ['SLACK_URL']
    webhook = WebhookClient(url)
    
    try:
        response = webhook.send(
            text="fallback",
            blocks=large_sample(event['detail'])
        )

        #assert response.status_code == 200
        #assert response.body == "ok"
    except:
        return {
            'statusCode': 400
        }
    
    else:
        return {
            'statusCode': 200
        }


def block_image():
    return [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "This is a section block with an accessory image."
			},
			"accessory": {
				"type": "image",
				"image_url": "https://pbs.twimg.com/profile_images/625633822235693056/lNGUneLX_400x400.jpg",
				"alt_text": "cute cat"
			}
		}
	]


def button():
    bucket='config-bucket-472520836625'
    return [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "This is a section block with a button to open a bucket."
			},
			"accessory": {
				"type": "button",
				"text": {
					"type": "plain_text",
					"text": "Open S3 Bucket",
					"emoji": True
				},
				"value": "click_me_123",
				"url": f"https://s3.console.aws.amazon.com/s3/buckets/{bucket}",
				"style": "primary",
				"action_id": "button-action"
			}
		}
	]


def large_sample(event):
    region = event.get('awsRegion')
    account = event.get('awsAccountId')
    rule_name = event.get('configRuleName')
    type_event = event.get('messageType')
    
    web_rule = f'https://{region}.console.aws.amazon.com/config/home?region={region}#/rules/details?configRuleName={rule_name}'
    
    return [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": f"Event type: *{type_event}* \nAccount: {account} \nRegion: {region} \nRule Name: _{rule_name}_"
			},
			"accessory": {
				"type": "image",
				"image_url": "https://awsvideocatalog.com/images/aws/png/PNG%20Light/Management%20&%20Governance/AWS-Config.png",
				"alt_text": "aws config"
			},
		},
  		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": event['newEvaluationResult']['annotation']
			}
		},
		{
			"type": "actions",
			"elements": [
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Link to AWS Config Rule",
						"emoji": True
					},
					"value": "click_me_123",
					"url": web_rule,
				}
			]
		},
  		{
			"type": "divider"
		}
	]
