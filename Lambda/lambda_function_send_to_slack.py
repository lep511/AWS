# pip install slack_sdk
# aws-security [slack]
# https://hooks.slack.com/services/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

import boto3
import json
import os
from slack_sdk.webhook import WebhookClient

url = os.environ['url']
webhook = WebhookClient(url)

def lambda_handler(event, context):
    
    response = webhook.send(
        text="fallback",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "You have a new request:\n*<https://amazon.com|Fred Enriquez - New device request>*"
                }
            }
        ]
    )
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }


"""
            {
              "type": "image",
              "image_url": "http://placekitten.com/700/500",
              "alt_text": "Multiple cute kittens"
            }
"""

"""
            {
            			"type": "section",
            			"text": {
            				"type": "plain_text",
            				"text": "I think it's super cool",
            				"emoji": True
            			}
            		},
            		{
            			"type": "video",
            			"title": {
            				"type": "plain_text",
            				"text": "How to use Slack.",
            				"emoji": True
            			},
            			"title_url": "https://www.youtube.com/watch?v=RRxQQxiM7AA",
            			"description": {
            				"type": "plain_text",
            				"text": "Slack is a new way to communicate with your team. It's faster, better organized and more secure than email.",
            				"emoji": True
            			},
            			"video_url": "https://www.youtube.com/embed/RRxQQxiM7AA?feature=oembed&autoplay=1",
            			"alt_text": "How to use Slack?",
            			"thumbnail_url": "https://i.ytimg.com/vi/RRxQQxiM7AA/hqdefault.jpg",
            			"author_name": "Arcado Buendia",
            			"provider_name": "YouTube",
            			"provider_icon_url": "https://a.slack-edge.com/80588/img/unfurl_icons/youtube.png"
            		}
"""
