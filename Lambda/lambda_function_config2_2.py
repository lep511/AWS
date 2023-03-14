# RULE UTIL
import json
import datetime
import boto3

# USE ENTIRE FILE AS IS

aws_config = boto3.client('config')

# Helper function used to validate input


def check_defined(reference, reference_name):
    if not reference:
        raise Exception('Error: ', reference_name, 'is not defined')
    return reference

# Check whether the message is OversizedConfigurationItemChangeNotification


def is_oversized_changed_notification(message_type):
    check_defined(message_type, 'messageType')
    return message_type == 'OversizedConfigurationItemChangeNotification'

# Get configurationItem using getResourceConfigHistory API.
# In case of OversizedConfigurationItemChangeNotification


def get_configuration(resource_type, resource_id, configuration_capture_time):
    result = aws_config.get_resource_config_history(
        resourceType=resource_type,
        resourceId=resource_id,
        laterTime=configuration_capture_time,
        limit=1)
    configuration_item = result['configurationItems'][0]
    return convert_api_configuration(configuration_item)

# Convert from the API model to the original invocation model


def convert_api_configuration(configuration_item):
    for k, v in configuration_item.items():
        if isinstance(v, datetime.datetime):
            configuration_item[k] = str(v)
    configuration_item['awsAccountId'] = configuration_item['accountId']
    configuration_item['ARN'] = configuration_item['arn']
    configuration_item['configurationStateMd5Hash'] = \
        configuration_item['configurationItemMD5Hash']
    configuration_item['configurationItemVersion'] = \
        configuration_item['version']
    configuration_item['configuration'] = \
        json.loads(configuration_item['configuration'])
    if 'relationships' in configuration_item:
        for i in range(len(configuration_item['relationships'])):
            configuration_item['relationships'][i]['name'] = \
                configuration_item['relationships'][i]['relationshipName']
    return configuration_item

# Based on the type of message get the configuration item either from
# configurationItem in the invoking event or using the
# getResourceConfigHistory API in getConfiguration function.


def get_configuration_item(invoking_event):
    check_defined(invoking_event, 'invoking_event')
    if is_oversized_changed_notification(invoking_event['messageType']):
        configuration_item_summary = check_defined(
            invoking_event['configurationItemSummary'],
            'configurationItemSummary')
        return get_configuration(
            configuration_item_summary['resourceType'],
            configuration_item_summary['resourceId'],
            configuration_item_summary['configurationItemCaptureTime'])
    else:
        return check_defined(
            invoking_event['configurationItem'],
            'configurationItem')

# Check whether the resource has been deleted.
# If it has, then the evaluation is unnecessary.


def is_applicable(configuration_item, event):
    check_defined(configuration_item, 'configurationItem')
    check_defined(event, 'event')
    status = configuration_item['configurationItemStatus']
    event_left_scope = event['eventLeftScope']
    return (status == 'OK' or status == 'ResourceDiscovered') \
        and event_left_scope is False

# This decorates the lambda_handler in rule_code with the
# actual PutEvaluation call


def rule_handler(lambda_handler):

    def handler_wrapper(event, context):
        check_defined(event, 'event')
        invoking_event = json.loads(event['invokingEvent'])
        rule_parameters = {}
        if 'ruleParameters' in event:
            rule_parameters = json.loads(event['ruleParameters'])
        configuration_item = get_configuration_item(invoking_event)
        invoking_event['configurationItem'] = configuration_item
        event['invokingEvent'] = json.dumps(invoking_event)
        compliance = 'NOT_APPLICABLE'
        if is_applicable(configuration_item, event):
            # Invoke the compliance checking function.
            compliance = lambda_handler(event, context)
        # Put together the request that reports the evaluation status
        evaluations = [{
            'ComplianceResourceType': configuration_item['resourceType'],
            'ComplianceResourceId': configuration_item['resourceId'],
            'ComplianceType': compliance,
            'OrderingTimestamp':
                configuration_item['configurationItemCaptureTime']
        }]
        result_token = event['resultToken']
        # Invoke the Config API to report the result of the evaluation
        aws_config.put_evaluations(
            Evaluations=evaluations,
            ResultToken=result_token)
        return compliance
    return handler_wrapper
