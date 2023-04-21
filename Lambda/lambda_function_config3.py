# RULE DESCRIPTION
# This example rule checks that EC2 instances are of the desired instance type
# The desired instance type is specified in the rule parameters.
#
# RULE DETAILS
# Trigger Type (Change Triggered or Periodic: Change Triggered)

# Required Parameters: desiredInstanceType - t3.micro
# Rule parameters are defined in template.yml

import json


# Add Scope of Changes e.g. ["AWS::EC2::Instance"] or 
# ["AWS::EC2::Instance","AWS::EC2::InternetGateway"]
APPLICABLE_RESOURCES = ["AWS::S3::Bucket"]

# This is where it's determined whether the resource is compliant or not.
# In this example, we simply decide that the resource is compliant if it 
# is an instance and its type matches the type specified as the desired type.
# If the resource is not an instance, then we deem this resource to be not
# applicable. (If the scope of the rule is specified to include only
# instances, this rule would never have been invoked.)


def evaluate_compliance(configuration_item, rule_parameters):
    if configuration_item['resourceType'] not in APPLICABLE_RESOURCES:
        print(configuration_item['resourceType'])
        return 'NOT_APPLICABLE'
    elif configuration_item['awsRegion'] != 'us-east-1':
        return 'NON_COMPLIANT'
    else:
        return 'COMPLIANT'

def lambda_handler(event, context):
    invoking_event = json.loads(event['invokingEvent'])
    configuration_item = invoking_event['configurationItem']
    rule_parameters = {}
    if 'ruleParameters' in event:
        rule_parameters = json.loads(event['ruleParameters'])
    return evaluate_compliance(configuration_item, rule_parameters)
