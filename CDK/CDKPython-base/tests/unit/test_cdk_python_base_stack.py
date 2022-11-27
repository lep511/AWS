import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_python_base.cdk_python_base_stack import CdkPythonBaseStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk_python_base/cdk_python_base_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CdkPythonBaseStack(app, "cdk-python-base")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
