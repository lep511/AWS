# Amazon CloudWatch C++ SDK code examples

## Purpose
The code examples in this directory demonstrate how to work with Amazon CloudWatch
using the AWS SDK for C++.

Amazon CloudWatch provides a reliable, scalable, and flexible monitoring solution that you can start using within minutes. 
You no longer need to set up, manage, and scale your own monitoring systems and infrastructure.

## Code examples

### API examples
- [Delete an alarm](./delete_alarm.cpp) (DeleteAlarms)
- [Describe alarms](./describe_alarms.cpp) (DescribeAlarms)
- [Disable alarm actions](./disable_alarm_actions.cpp) (DisableAlarmActions)
- [Enable alarm actions](./enable_alarm_actions.cpp) (EnableAlarmActions)
- [List metrics](./list_metrics.cpp) (ListMetrics)
- [Put metric alarm](./put_metric_alarm.cpp) (PutMetricAlarm)
- [Put metric data](./put_metric_data.cpp) (PutMetricData)

## ⚠ Important
- We recommend that you grant your code least privilege, or at most the minimum permissions required to perform the task. For more information, see [Grant Least Privilege](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html#grant-least-privilege) in the AWS Identity and Access Management User Guide.
- This code has not been tested in all AWS Regions. Some AWS services are available only in specific [Regions](https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services).
- Running this code might result in charges to your AWS account. 

## Running the examples

### Prerequisites
- An AWS account. To create an account, see [How do I create and activate a new AWS account](https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/) on the AWS Premium Support website.
- Complete the installation and setup steps of [Getting Started](https://docs.aws.amazon.com/sdk-for-cpp/v1/developer-guide/getting-started.html) in the AWS SDK for C++ Developer Guide.
The Getting Started section covers how to obtain and build the SDK, and how to build your own code utilizing the SDK with a sample "Hello World"-style application. 
- See [Getting started with the AWS SDK for C++ code examples](https://docs.aws.amazon.com/sdk-for-cpp/v1/developer-guide/getting-started-code-examples.html) for information on the structure of the code examples, building, and running the examples.

To run these code examples, your AWS user must have permissions to perform these actions with Amazon CloudWatch.  
The AWS managed policy named "CloudWatchFullAccess" may be used to bulk-grant the necessary permissions.  
For more information on attaching policies to IAM user groups, 
see [Attaching a policy to an IAM user group](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_groups_manage_attach-policy.html).

## Resources
- [AWS SDK for C++ Documentation](https://docs.aws.amazon.com/sdk-for-cpp/index.html) 
- [Amazon CloudWatch Documentation](https://docs.aws.amazon.com/cloudwatch/)
