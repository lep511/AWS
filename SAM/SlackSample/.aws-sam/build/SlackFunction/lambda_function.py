# Link: https://api.slack.com/tools/block-kit-builder
import json
import sys
import os
from slack_sdk.webhook import WebhookClient

# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

config_icon = "https://awsvideocatalog.com/images/aws/png/PNG%20Light/Management%20&%20Governance/AWS-Config.png"
security_hub_icon = "https://d2908q01vomqb2.cloudfront.net/22d200f8670dbdb3e253a90eee5098477c95c23d/2022/12/13/SecurityHublogo.jpg"


def lambda_handler(event, context):
    print(event)
    event_source = event.get('source')
    
    # AWS Config
    if event_source == 'aws.config':
        config_event(event['detail'])
    # AWS Security Hub
    elif event_source == 'aws.securityhub':
        security_hub(event['detail'])
    # If not recognized service
    else:
        return {
            'statusCode': 401
        }
    return {
        'statusCode': 200
    }

def security_hub(event):
    # Findings
    for finding in event['findings']:
        region = finding.get('Region')
        account = finding.get('AwsAccountId')
        resource_id = finding['Resources'][0]['Id']

        main_txt = f"*Account:* {account} \n*Region:* {region}"
        main_txt += f"\n*Resource Id:* {resource_id}"
        
        description = finding['Description']
        try:
            web_rule = finding['Remediation']['Recommendation']['Url']
        except:
            web_rule = 'https://www.google.com'
        
        button_text = "Link to remediation steps"
        
        response = response_slack(main_txt, description, web_rule, security_hub_icon, button_text)
        send_to_slack(response)
        

def config_event(event):
    region = event.get('awsRegion')
    account = event.get('awsAccountId')
    rule_name = event.get('configRuleName')
    type_event = event.get('messageType')
    new_eval_result = event.get('newEvaluationResult')
    resource_type = event['newEvaluationResult']['evaluationResultIdentifier']['evaluationResultQualifier']['resourceType']
    resource_id = event['newEvaluationResult']['evaluationResultIdentifier']['evaluationResultQualifier']['resourceId']
    description = event['newEvaluationResult'].get('annotation')
    main_txt = f"*Event type:* {type_event} \n*Account:* {account} \n*Region:* {region} \n*Resource Type:* {resource_type}"
    main_txt += f"\n*Resource Id:* {resource_id} \n*Rule Name:* _{rule_name}_"

    web_rule = f'https://{region}.console.aws.amazon.com/config/home?region={region}#/rules/details?configRuleName={rule_name}'
    button_text = "Link to AWS Config Rule"
    
    response = response_slack(main_txt, description, web_rule, config_icon, button_text)
    send_to_slack(response)


def response_slack(main_txt, description, web_rule, icon, button_text):
    return [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": main_txt
			},
			"accessory": {
				"type": "image",
				"image_url": icon,
				"alt_text": "icon"
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
						"text": button_text,
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


def send_to_slack(event_response):
    url = os.environ['SLACK_URL']
    webhook = WebhookClient(url)
    
    try:
        response_slack = webhook.send(
            text="fallback",
            blocks=event_response
        )
        assert response_slack.status_code == 200
        assert response_slack.body == "ok"
        print(f"[INFO] {response_slack.body}")
    
    except Exception as e:
        print(f"[ERROR] {e}")