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
inspector_icon = "https://help.sumologic.com/img/integrations/amazon-aws/inspector-classic.png"
guardduty_icon = "https://awsvideocatalog.com/images/aws/png/PNG%20Light/Security,%20Identity,%20&%20Compliance/Amazon-GuardDuty.png"
iam_analyzer_icon = "https://www.checkpoint.com/wp-content/uploads/amazon-aws-security-iam-analyzer-icon.png"
macie_icon = "https://awsvideocatalog.com/images/aws/png/PNG%20Light/Security,%20Identity,%20&%20Compliance/Amazon-Macie.png"


def lambda_handler(event, context):
    print(event)
    event_source = event.get('source')
    
    # AWS Config
    if event_source == 'aws.config':
        title = event.get('detail-type')
        config_event(event['detail'], title)
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
        web_rule = 'https://www.google.com'
        button_text = "Google"
        title = finding['Title']
        region = finding.get('Region')
        account = finding.get('AwsAccountId')
        product_name = finding['ProductName']
        resource_id = finding['Resources'][0]['Id']
        severity = finding['Severity']['Label']

        main_txt = f"*{title}*"
        main_txt += f"\n\n• *Product Name:* {product_name}"
        main_txt += f"\n• *Account:* {account} \n• *Region:* {region}"
        main_txt += f"\n• *Severity:* {severity} \n• *Resource Id:* {resource_id}"
        
        description = finding['Description']
        
        # Filter by product name and set web icon
        if 'Remediation' in finding:
            if 'Url' in finding['Remediation']['Recommendation']:
                web_rule = finding['Remediation']['Recommendation']['Url']
                button_text = "Link to remediation steps"
            elif 'Text' in finding['Remediation']['Recommendation']:
                description += f"\n\n• *Recommendation:* {finding['Remediation']['Recommendation']['Text']}"
                if 'SourceUrl' in finding:
                    web_rule = finding['SourceUrl']
                    button_text = "Link to finding"
        
        elif 'SourceUrl' in finding:
            web_rule = finding['SourceUrl']
            button_text = "Link to finding"
        
        # Filter by product name and set icon
        if finding['ProductName'] == 'Config':
            image_icon = config_icon
            icon_text = "AWS Config"
        elif finding['ProductName'] == 'Inspector':
            image_icon = inspector_icon
            icon_text = "AWS Inspector"
        elif finding['ProductName'] == 'GuardDuty':
            image_icon = guardduty_icon
            icon_text = "AWS GuardDuty"
        elif finding['ProductName'] == 'IAM Access Analyzer':
            image_icon = iam_analyzer_icon
            icon_text = "AWS IAM Access Analyzer"
        elif finding['ProductName'] == 'Macie':
            image_icon = macie_icon
            icon_text = "AWS Macie"
            bucket_name = resource_id.split(':')[-1]
            web_rule = f"https://s3.console.aws.amazon.com/s3/buckets/{bucket_name}?region={region}"
            button_text = "Link to S3 Bucket"
        else:
            image_icon = security_hub_icon
            icon_text = "AWS Security Hub"
        
        response = response_slack(main_txt, description, web_rule, image_icon, button_text, icon_text)
        send_to_slack(response)
        

def config_event(event, title=None):
    region = event.get('awsRegion')
    account = event.get('awsAccountId')
    rule_name = event.get('configRuleName')
    type_event = event.get('messageType')
    new_eval_result = event.get('newEvaluationResult')
    resource_type = event['newEvaluationResult']['evaluationResultIdentifier']['evaluationResultQualifier']['resourceType']
    resource_id = event['newEvaluationResult']['evaluationResultIdentifier']['evaluationResultQualifier']['resourceId']
    description = event['newEvaluationResult'].get('annotation')
    main_txt = f"*{title}*\n\n• *Product Name:* AWS Config"
    main_txt += f"\n• *Event type:* {type_event} \n• *Account:* {account} \n• *Region:* {region} \n• *Resource Type:* {resource_type}"
    main_txt += f"\n• *Resource Id:* {resource_id} \n• *Rule Name:* _{rule_name}_"

    web_rule = f'https://{region}.console.aws.amazon.com/config/home?region={region}#/rules/details?configRuleName={rule_name}'
    button_text = "Link to AWS Config Rule"
    
    response = response_slack(main_txt, description, web_rule, config_icon, button_text)
    send_to_slack(response)


def response_slack(main_txt, description, web_rule, icon, button_text, icon_text="aws service"):
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
				"alt_text": icon_text
			},
		},
  		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": f"• *Description:* {description}"
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