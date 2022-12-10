import cfnresponse
import boto3

iam_client = boto3.client("iam")
lambda_client = boto3.client("lambda")

def attach_policies(role_name, policy_arns):
    for policy_arn in policy_arns:
        iam_client.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)

def delete_attach_policies_policy():
    iam_client.delete_role_policy(RoleName="AttachPolicies", PolicyName="AttachPolicies")

def delete_function_and_role():
    lambda_client.delete_function(FunctionName="AttachPolicies")
    iam_client.delete_role_policy(RoleName="AttachPolicies", PolicyName="DeleteResources")
    iam_client.delete_role(RoleName="AttachPolicies")

def handler(event, context):
    properties = event["ResourceProperties"]
    try:
        if event["RequestType"] == "Create":
            attach_policies(properties["RoleName"], properties["PolicyArns"])
            delete_attach_policies_policy()
            reason = "Policies Attached"
        else:
            reason = "No Action Performed"
        status = cfnresponse.SUCCESS
    except Exception as e:
        status = cfnresponse.FAILED
        reason = str(e)[:500]
    finally:
        cfnresponse.send(event, context, status, {}, reason=reason)
        delete_function_and_role()