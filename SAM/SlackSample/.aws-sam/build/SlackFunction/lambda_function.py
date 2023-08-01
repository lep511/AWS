# Link: https://api.slack.com/tools/block-kit-builder
import json
import sys
from slack_sdk.webhook import WebhookClient

# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)


def lambda_handler(event, context):
    url = 'https://hooks.slack.com/services/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'
    webhook = WebhookClient(url)
    
    try:
        
        response = webhook.send(
            text="fallback",
            blocks=large_sample()
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


def large_sample():
    return [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "Hello, Assistant to the Regional Manager Dwight! *Michael Scott* wants to know where you'd like to take the Paper Company investors to dinner tonight.\n\n *Please select a restaurant:*"
			}
		},
		{
			"type": "divider"
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*Farmhouse Thai Cuisine*\n:star::star::star::star: 1528 reviews\n They do have some vegan options, like the roti and curry, plus they have a ton of salad stuff and noodles can be ordered without meat!! They have something for everyone here"
			},
			"accessory": {
				"type": "image",
				"image_url": "https://awsvideocatalog.com/images/aws/png/PNG%20Light/Management%20&%20Governance/AWS-Config.png",
				"alt_text": "alt text for image"
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*Kin Khao*\n:star::star::star::star: 1638 reviews\n The sticky rice also goes wonderfully with the caramelized pork belly, which is absolutely melt-in-your-mouth and so soft."
			},
			"accessory": {
				"type": "image",
				"image_url": "https://awsvideocatalog.com/images/aws/png/PNG%20Light/Management%20&%20Governance/AWS-Config.png",
				"alt_text": "alt text for image"
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*Ler Ros*\n:star::star::star::star: 2082 reviews\n I would really recommend the  Yum Koh Moo Yang - Spicy lime dressing and roasted quick marinated pork shoulder, basil leaves, chili & rice powder."
			},
			"accessory": {
				"type": "image",
				"image_url": "https://awsvideocatalog.com/images/aws/png/PNG%20Light/Management%20&%20Governance/AWS-Config.png",
				"alt_text": "alt text for image"
			}
		},
		{
			"type": "divider"
		},
		{
			"type": "actions",
			"elements": [
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Farmhouse",
						"emoji": True
					},
					"value": "click_me_123"
				},
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Kin Khao",
						"emoji": True
					},
					"value": "click_me_123",
					"url": "https://google.com"
				},
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Ler Ros",
						"emoji": True
					},
					"value": "click_me_123",
					"url": "https://google.com"
				}
			]
		}
	]
