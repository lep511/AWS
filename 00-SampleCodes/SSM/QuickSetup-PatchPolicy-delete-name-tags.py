# Copyright 2022 Amazon.com, Inc. or its affiliates. All Rights Reserved.

# This handler responds to a Cloud Formation Stack 'DELETE' notification. 
# It is responsible for detaching all name tags from target nodes, including
# nodes that are no longer a target of the Quick Setup Configuration but for which
# drift has not yet been remediated.
from asyncore import poll
from botocore.exceptions import ClientError
import boto3
import json
from urllib.request import build_opener, HTTPHandler, Request
import os
import time

# ENVIRONMENT VARIABLES
region = os.environ['REGION']

# CONSTANTS
MINUTES_FOR_POLLING_COMPLETION = 600 # 10 hrs max.
ASSOCIATION_NON_TERMINAL_STATUSES = ["Pending", "InProgress"]
DESCRIBE_ASSOCIATION_KEYS = ["AssociationId","Parameters","DocumentVersion","ScheduleExpression",\
    "OutputLocation","Name","Targets","AssociationName","AssociationVersion","AutomationTargetParameterName",\
    "MaxErrors","MaxConcurrency","ComplianceSeverity","SyncCompliance","ApplyOnlyAtCronInterval","CalendarNames",\
    "TargetLocations"]

# CLIENTS
client = boto3.client('ssm', region_name= region)  

def build_request(event,status, message):
    try:
        stack_id = check_for_key(event, 'StackId')
        request_id = check_for_key(event, 'RequestId')
        logical_resource_id = check_for_key(event, 'LogicalResourceId')

        body = json.dumps({        
            'Status': status,        
            'Reason': message,        
            'StackId': stack_id,
            'RequestId': request_id,
            'LogicalResourceId': logical_resource_id,
            'PhysicalResourceId': 'associationId'})
     
        request = Request(check_for_key(event, 'ResponseURL'), data=body.encode('utf-8'))
        request.add_header('Content-Type', '')
        request.add_header('Content-Length', len(body.encode('utf-8')))
        request.get_method = lambda: 'PUT'
        return request
    except Exception as ex:
        raise Exception("An Exception occurred while building a response for Cloud Formation. %s"%(str(ex)))

def poll_for_association_completion(event, association_ids):
    for id in association_ids:
        counter = 0
        while True:
            print("Polling for Association completion: %s"%(id))
            response = client.describe_association_executions(AssociationId=id)
            print("DescribeAssociationExecution result: %s"%(str(response)))
            ## check status, exit if good
            executions = response["AssociationExecutions"]
            if (len(executions) < 1):
                msg = "Association %s has never been executed. Something went wrong. "%(id)
                send_response(event, "FAILED", msg)
                return False
            else:
                status = executions[0]["Status"]
                print("Found status of %s for latest execution of %s"%(status, id))
                # Association Execution History is always reported in descending order. 
                if (status in ASSOCIATION_NON_TERMINAL_STATUSES):
                    print("Association %s is %s . Waiting 5 seconds. "%(id, executions[0]["Status"]))
                    time.sleep(5)
                    counter +=1

                    if counter == MINUTES_FOR_POLLING_COMPLETION:
                        msg = "Association has not finished in the required time. Exiting."
                        send_response(event, "FAILED", msg)
                        return False
                else:
                    # if the status is not success, fail the Lambda. 
                    if (status.lower() != "success"):
                        msg = "Association %s returned a non-success status of %s."%(id, status)
                        send_response(event, "FAILED", msg)
                        return False
                    else:
                        print("Association %s completed successfully."%(id))
                        return True

def build_opener_and_open(request):
    opener = build_opener(HTTPHandler)
    response = opener.open(request) 
    return response

def send_response(event, status, message, count = 0):
    try:
        request = build_request(event, status, message)
        response = build_opener_and_open(request)
        # This snippet is the reason behind not using the cfnresponse python module
        # found here: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-lambda-function-code-cfnresponsemodule.html
        # The cfnresponse python module simply print's an http status code error and succeeds. 
        # The desired behavior is for the Lambda to fail if the response code is not 200.
        # technically, this response status should be a string but the urllib library doesn't say
        # if it is translated to a string or not.
        if str(response.status) != "200":
            raise Exception("Received a failed response from Cloud Formation: %s"%(str(response.status)))
    except Exception as ex:
        print("An Exception occured while sending a response to Cloud Formation. ")
        if count < 3:
            count +=1
            send_response(event, status, message, count)
        else:
            raise Exception("Retries failed. Failing Lambda execution.")


def check_for_key(hash, key):
    if not key in hash:
        raise Exception("The required key %s is not present in %s. Failing."%(key, str(hash)))
    else:
        # return the value
        return hash[key]

def update_association(event, association_id):

    print("Describing association %s for update command."%(association_id))
    response = client.describe_association(AssociationId=association_id)
    print(response)

    association = response['AssociationDescription']
    print("Using Association Overview %s: "%(str(association)))
    print("Stripping described association of keys that cannot be used in update command.")
    keys_to_pop = []
    [keys_to_pop.append(key) if key not in DESCRIBE_ASSOCIATION_KEYS else print(key) for key in association]
    [association.pop(key) for key in keys_to_pop]

    # Postfix name with -delete for easy identification. 
    association["AssociationName"] = association["AssociationName"] + "-DELETE"

    # TAG DOCUMENT
    if "TagAction" in association["Parameters"]:
        association["AutomationTargetParameterName"] = "InstanceId"
        association["Targets"] = association["Targets"]
        association["Parameters"]["TagAction"] = ["Remove"]
    else: 
        # REMEDIATION DOCUMENT
        # Remediation document uses the NoOp Automation target tag which State Manager does not
        # comprehend as a parameter and only adds if the following parameters are not present.
        if "Targets" in association: 
            association.pop("Targets")

    print("Attempting to update association %s"%(association))
    response = client.update_association(**association)
    print("UpdateResponse: %s"%(str(response)))

def handler(event, context):      
    try:
        print("Received event %s"%(str(event)))
    
        request = None
        request = check_for_key(event, 'RequestType')

        if (request == None or request.lower() != 'delete'):
            msg = "Received a %s request. Tag Detach Machine only handles CF Stack 'Delete' events. Succeeding."%(str(request))
            send_response(event, "SUCCESS", msg)
            return

        resource_properties = check_for_key(event, "ResourceProperties")

        tag_association_id =check_for_key(resource_properties, 'TagAssociationId')
        remediation_association_id = check_for_key(resource_properties, 'RemediationAssociationId')

        # Now update the associations to have the names postfixed with DELETE and trigger a name tag delete.
        update_association(event, tag_association_id)
        update_association(event, remediation_association_id)

        # Giving Association time to update and trigger new executions.
        print("Sleeping to give Association time to update: %s"%(time.ctime()))
        time.sleep(15)
        print("Done sleeping: %s"%(time.ctime()))

        #Now poll for the associations to finish
        success = poll_for_association_completion(event, [tag_association_id, remediation_association_id])       

        if success == True:
            # Once the associations have finished.
            send_response(event, "SUCCESS", "Association's successfully completed. Exiting Lambda.")
        else:
            msg = "Name tags failed to delete. Retaining resources so customer can trigger a delete after the fact."
            send_response(event, "FAILED", "%s:"%(msg))

    except Exception as e:
        send_response(event, "FAILED", "%s:"%(str(e)))
        raise(e)
