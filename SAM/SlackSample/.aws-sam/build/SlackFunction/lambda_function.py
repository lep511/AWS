# Link: https://api.slack.com/tools/block-kit-builder
import json
import sys
import os
from slack_sdk.webhook import WebhookClient

# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)


def lambda_handler(event, context):
    print(event)
    url = os.environ['SLACK_URL']
    webhook = WebhookClient(url)
    event_source = event.get('source')
    
    if event_source == 'aws.config':
        event_response = config_event(event['detail'])
    else:
        return {
            'statusCode': 401
        }
    
    try:
        response = webhook.send(
            text="fallback",
            blocks=event_response
        )
        assert response.status_code == 200
        assert response.body == "ok"
    
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


def config_event(event):
    
    region = event['awsRegion']
    account = event['awsAccountId']
    rule_name = event['configRuleName']
    type_event = event['messageType']
    new_eval_result = event['newEvaluationResult']
    resource_type = event['newEvaluationResult']['evaluationResultIdentifier']['evaluationResultQualifier']['resourceType']
    resource_id = event['newEvaluationResult']['evaluationResultIdentifier']['evaluationResultQualifier']['resourceId']
    description = event['newEvaluationResult']['annotation']
    main_txt = f"*Event type:* {type_event} \n*Account:* {account} \n*Region:* {region} \n*Resource Type:* {resource_type}"
    main_txt += f"\n*Resource Id:* {resource_id} \n*Rule Name:* _{rule_name}_"
    
    web_rule = f'https://{region}.console.aws.amazon.com/config/home?region={region}#/rules/details?configRuleName={rule_name}'
    
    return [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": main_txt
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
				"text": f"*Description:* {description}"
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
