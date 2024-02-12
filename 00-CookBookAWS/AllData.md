## AWS CloudFormation

This application uses [AWS CloudFormation](https://aws.amazon.com/cloudformation/) to define and deploy the application to AWS. This page includes patterns and best practices for working with CloudFormation that are used in this application. Note, if you are new to AWS CloudFormation, you may want to read [this introduction page](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/Welcome.html) from the AWS CloudFormation User Guide before continuing.

- [Organize resources into nested stacks](#organize-resources-into-nested-stacks)
- [Use pseudo parameters for increased portability](#use-pseudo-parameters-for-increased-portability)
- [Let CloudFormation generate resource names](#let-cloudFormation-generate-resource-names)
- [Referencing Stack Resources](#referencing-stack-resources)

## Organize resources into nested stacks

More complex component stacks use [nested stacks](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-nested-stacks.html) to organize the resources within that component. For example, the backend stack has a nested stack for API resources and another one for database resources. Similarly, the ops stack has a nested stack for alarms and another one for dashboards.

In addition to general organization of resources, nested stacks are also useful for

1. helping you to avoid hitting the CloudFormation [stack resource limit](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html). This is very important since CloudFormation does not support refactoring resources between stacks, so fixing this after hitting the limit can be painful.
1. tagging a group of related resources with the same AWS tags. When you tag a nested stack, the same tags are applied to all resources within the nested stack that support tagging.

**Note:** In this example application, the DynamoDB table storing the backend data is created in a nested stack along with the rest of the backend top-level stack. However, some teams opt to create their database resources in a completely separate top-level stack with its own CD pipeline in order to minimize deployments to database resources.

**Examples in this project:**

1. The backend template [contains nested stacks](https://github.com/awslabs/realworld-serverless-application/blob/c0e5397e252522da055d50d7da8b892f1bb10d36/backend/sam/app/template.yaml#L27-L39) organizing [API resources](https://github.com/awslabs/realworld-serverless-application/blob/c0e5397e252522da055d50d7da8b892f1bb10d36/backend/sam/app/api.template.yaml) and [database resources](https://github.com/awslabs/realworld-serverless-application/blob/c0e5397e252522da055d50d7da8b892f1bb10d36/backend/sam/app/database.template.yaml) into separate nested stacks.
1. The ops template [contains nested stacks](https://github.com/awslabs/realworld-serverless-application/blob/c0e5397e252522da055d50d7da8b892f1bb10d36/ops/sam/app/template.yaml#L27-L38) organizing [alarm resources](https://github.com/awslabs/realworld-serverless-application/blob/c0e5397e252522da055d50d7da8b892f1bb10d36/ops/sam/app/alarm.template.yaml) and [dashboard resources](https://github.com/awslabs/realworld-serverless-application/blob/c0e5397e252522da055d50d7da8b892f1bb10d36/ops/sam/app/dashboard.template.yaml) into separate nested stacks.

## Use pseudo parameters for increased portability

Pseudo parameters are parameters that are predefined by AWS CloudFormation. You do not declare them in your template. Use them the same way as you would a parameter, as the argument for the `Ref` function. Pseudo parameters are useful for making your template portable so you can use it to deploy stacks in different accounts, regions, and even AWS partitions, e.g., AWS GovCloud regions. Pseudo parameters like `AWS::AccountId`, `AWS::Region`, and `AWS::Partition` should be used in place of hardcoded values whenever possible. To learn more about CloudFormation pseudo parameters, see the [AWS CloudFormation User Guide](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/pseudo-parameter-reference.html).

**Examples in this project:**

1. [Setting the access log destination log group ARN](https://github.com/awslabs/aws-serverless-app-repo-reference-implementation/blob/0d97eaf56b2320ce961c1e033733fc06a32b3858/aws-serverless-app-repo-reference-backend/sam/app/api.template.yaml#L49)
1. [Mapping an API Gateway resource method to a Lambda function](https://github.com/awslabs/aws-serverless-app-repo-reference-implementation/blob/0d97eaf56b2320ce961c1e033733fc06a32b3858/aws-serverless-app-repo-reference-backend/swagger/api.yaml#L78)

## Let CloudFormation generate resource names

In CloudFormation, you can define explicit names for resources, such as the name of an Amazon DynamoDB table. However, if you choose not to fill in an explicit name for a resource, CloudFormation will generate a unique resource name for you. In general, it is better to let CloudFormation name resources for you. This ensures the template is portable and can be used to deploy multiple stacks in the same account/region without encountering a name conflict error.

CloudFormation's automatic naming algorithm also takes into account naming constraints for specific resource types. For example, S3 bucket names have many constraints such as compliance with DNS naming conventions and not allowing uppercase letters.

To learn more about CloudFormation resource names, see the [AWS CloudFormation User Guide](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-name.html).

## Referencing Stack Resources

When using CloudFormation to provision AWS resources for your application, you will need to reference the names and attributes of resources created by CloudFormation in your CloudFormation templates as well as within your Lambda function code, e.g., specifying the name of a DynamoDB table to read/write.

CloudFormation provides a number of tools for referencing resource attributes within templates and Lambda functions, but it can be unclear which tools to use in which situations. Here are the best practices we've learned when building a complex serverless application:

### Share application resource attributes via SSM Parameter Store

In general, application resource attributes that need to be referenced elsewhere in the application should be saved in [AWS SSM Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html). There are several advantages to using SSM Parameter Store:

1. Its default tier is free and allows up to 10,000 parameters to be stored.
1. It supports parameter hierarchies, making it easy to organize parameters and also bulk fetch all parameters for an application.
1. It supports parameter value history for easy auditing.
1. CloudFormation supports creating SSM parameters and using dynamic references to retrieve parameter values and embed them into your template.
1. You can pass more parameter values to a Lambda function via SSM Parameter Store than Lambda environment variables, which have a 4KB limit. Also, Lambda environment variables are not supported in all regions where Lambda is supported, e.g., China regions.

SSM parameters allow you to share application resource attributes across stack templates and within your Lambda function code.

Some things to note about using SSM Parameter Store:

1. Due to [SSM Parameter Store's API throughput limits](https://docs.aws.amazon.com/general/latest/gr/aws_service_limits.html#limits_ssm), it is important to use a caching client library when retrieving SSM parameters. For example, [aws-ssm-java-caching-client](https://github.com/awslabs/aws-ssm-java-caching-client) is an SSM Parameter Store caching client library for Java and [ssm-cache-python](https://github.com/alexcasalboni/ssm-cache-python) is an SSM Parameter Store caching client library for Python.
1. CloudFormation's `AWS::SSM::Parameter` resource type cannot be used to create SecureString (encrypted) parameters. While CloudFormation resource attributes are ok to store in plain text in SSM Parameter Store, if your template has sensitive data passed as a parameter which needs to be stored, you can store it in [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/) using the `AWS::SecretsManager::Secret` resource type.

**Examples in this project:**

1. [Saving the Applications DynamoDB table name to SSM](https://github.com/awslabs/realworld-serverless-application/blob/6d0e3850b3da966ff0c953e18701847efbebe4d1/backend/sam/app/database.template.yaml#L51-L57) and [referencing it in a different stack template](https://github.com/awslabs/realworld-serverless-application/blob/6d0e3850b3da966ff0c953e18701847efbebe4d1/backend/sam/app/api.template.yaml#L90) as well as [retrieving it within Lambda function code](https://github.com/awslabs/realworld-serverless-application/blob/6d0e3850b3da966ff0c953e18701847efbebe4d1/backend/src/main/java/com/amazonaws/serverless/apprepo/container/config/SsmConfigProvider.java#L23-L25).
1. [Saving the Applications DynamoDB table stream ARN to SSM](https://github.com/awslabs/realworld-serverless-application/blob/6d0e3850b3da966ff0c953e18701847efbebe4d1/backend/sam/app/database.template.yaml#L65-L71) and [referencing it in the analytics stack template](https://github.com/awslabs/realworld-serverless-application/blob/6d0e3850b3da966ff0c953e18701847efbebe4d1/analytics/sam/app/template.yaml#L19) to attach a DDB stream fanout app to it.

### Exception: Generic, reusable templates

SSM Parameter Store works best when sharing resources across a specific application, like the one in this project. However, you can also create a CloudFormation template that represents a generic, self-contained "app" which is meant to be reused across many applications. Apps like these can be published to the [AWS Serverless Application Repository](https://aws.amazon.com/serverless/serverlessrepo/) and embedded in applications as [nested applications](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-template-nested-applications.html).

Since these kinds of self-contained apps are generally special-purpose and small, they can use Lambda function environment variables internally and CloudFormation [template outputs](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/outputs-section-structure.html) to surface resource attributes to the parent template that is nesting them. The parent template could then choose to save one of the outputs to SSM Parameter Store if it wanted to share it more widely across the rest of the application.

**Examples in this project:**

1. The analytics stack [nests the general purpose aws-dynamodb-stream-eventbridge-fanout app](https://github.com/awslabs/realworld-serverless-application/blob/6d0e3850b3da966ff0c953e18701847efbebe4d1/analytics/sam/app/template.yaml#L12-L19) from the AWS Serverless Application Repository. The app attaches to the given DynamoDB stream ARN and forwards events to [AWS EventBridge](https://aws.amazon.com/eventbridge/). 
1. Since the [aws-dynamodb-stream-eventbridge-fanout app](https://github.com/awslabs/aws-dynamodb-stream-eventbridge-fanout) is written to be generic and reusable, it uses Lambda environment variables [to pass resource attributes to its internal Lambda function](https://github.com/awslabs/aws-dynamodb-stream-eventbridge-fanout/blob/36726ec305b74e146db9ac06053bb9f99ce4c219/sam/app/template.yaml#L44-L48) and [surfaces attributes to the parent template via template outputs](https://github.com/awslabs/aws-dynamodb-stream-eventbridge-fanout/blob/36726ec305b74e146db9ac06053bb9f99ce4c219/sam/app/template.yaml#L69-L75).

## DynamoDB

This application uses [Amazon DynamoDB](https://aws.amazon.com/dynamodb/) as the backend database supporting the REST API. DynamoDB is a great choice for serverless APIs, because it is feature-rich and delivers single-digit millisecond performance at any scale. The DynamoDB Developer Guide already includes an extensive [best practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html) section, so this page will focus on specific best practices used by this application.

- [Configure auto-scaling](#configure-auto-scaling)
- [Enable encryption at rest](#enable-encryption-at-rest)
- [Enable point-in-time recovery (PITR)](#enable-point-in-time-recovery-pitr)
- [Enable DynamoDB streams for async processing](#enable-dynamodb-streams-for-async-processing)

## Configure auto-scaling

While DynamoDB does allow manually passing provisioned throughput values, it is much preferred to setup autoscaling to scale up read/write throughput as traffic increases to maintain availability and scale down read/write throughput as traffic decreases to reduce cost. The simplest auto-scaling solution for DynamoDB is to enable on-demand billing mode. To learn more about DynamoDB read/write capacity options, see the DynamoDB [Developer Guide](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ReadWriteCapacityMode.html).

**Examples in this project:**

1. [Setting on-demand billing mode](https://github.com/awslabs/realworld-serverless-application/blob/850ddf56764e59e1dd4ca2c40fd5bc8130061313/backend/sam/app/database.template.yaml#L43)

## Enable encryption at rest

DynamoDB's encryption at rest is a simple configuration option that allows you to build security-sensitive applications that meet strict encryption compliance and regulatory requirements. To learn more about DynamoDB encryption at rest, see the DynamoDB [Developer Guide](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/EncryptionAtRest.html).

**Examples in this project:**

1. [Setting encryption at rest](https://github.com/awslabs/realworld-serverless-application/blob/850ddf56764e59e1dd4ca2c40fd5bc8130061313/backend/sam/app/database.template.yaml#L44-L46)

## Enable point-in-time recovery (PITR)

Point-in-time recovery helps protect your DynamoDB tables from accidental write or delete operations, allowing you to restore a table to any point in time during the last 35 days. To learn more about DynamoDB point-in-time recovery, see the DynamoDB [Developer Guide](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/PointInTimeRecovery.html).

**Examples in this project:**

1. [Enabling point-in-time recovery](https://github.com/awslabs/realworld-serverless-application/blob/850ddf56764e59e1dd4ca2c40fd5bc8130061313/backend/sam/app/database.template.yaml#L47-L48)

## Enable DynamoDB streams for async processing

DynamoDB streams allow you to asynchronously process table updates. This can be useful for many operations, for example, analytics data processing. To learn more about DynamoDB streams, see the DynamoDB [Developer Guide](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Streams.html).

**Examples in this project:**

1. [Enabling streams](https://github.com/awslabs/realworld-serverless-application/blob/850ddf56764e59e1dd4ca2c40fd5bc8130061313/backend/sam/app/database.template.yaml#L38-L39)

## API Gateway

This application uses [Amazon API Gateway](https://aws.amazon.com/api-gateway/) for the backend REST API. Each REST endpoint is configured to invoke an [AWS Lambda](https://aws.amazon.com/lambda/) function to process each request. This page includes patterns and best practices for working with Amazon API Gateway that are used in this application.

- [Define your API using OpenAPI 3](#define-your-api-using-openapi-3)
- [Set API throttling limits](#set-api-throttling-limits)
- [Enable API logging](#enable-api-logging)
- [Use Amazon API Gateway to generate client SDKs](#use-amazon-api-gateway-to-generate-client-sdks)

## Define your API using OpenAPI 3

[OpenAPI](https://swagger.io/docs/specification/about/) is an API description format for REST APIs. It allows you to define your API endpoints, operations, and authentication methods in a single, declarative file. Defining your API using OpenAPI has several advantages:

1. OpenAPI is an open standard and includes useful tooling support, such as [an editor](https://swagger.io/tools/swagger-editor/) and [code generation tools](https://swagger.io/tools/swagger-codegen/) for generating language-specific code to support implementing the API.
1. Amazon API Gateway natively supports creating a REST API from an OpenAPI 3 definition. Amazon API Gateway has also extended the OpenAPI format, which allows defining Amazon API Gateway specific information in the same OpenAPI definition file.

### Use Amazon API Gateway OpenAPI extensions

Amazon API Gateway provides extensions to the OpenAPI specification allowing you to define API integrations, authorizers, and request validation.

**Examples in this project:**

1. [Map an API operation to the Lambda function](https://github.com/awslabs/realworld-serverless-application/blob/850ddf56764e59e1dd4ca2c40fd5bc8130061313/backend/swagger/api.yaml#L76-L81) that should be invoked to process the operation.
1. [Define constraints on API input parameters](https://github.com/awslabs/realworld-serverless-application/blob/850ddf56764e59e1dd4ca2c40fd5bc8130061313/backend/swagger/api.yaml#L380-L389) and then [enable API Gateway request validation](https://github.com/awslabs/realworld-serverless-application/blob/850ddf56764e59e1dd4ca2c40fd5bc8130061313/backend/swagger/api.yaml#L9-L14). API Gateway will automatically check API inputs based on the constraints defined in the OpenAPI definition and if validation fails, it will automatically return a 400 error back to the client without invoking your Lambda function to process the request. Caveat: You must [specify an error message](https://github.com/awslabs/realworld-serverless-application/blob/850ddf56764e59e1dd4ca2c40fd5bc8130061313/backend/swagger/api.yaml#L17-L20) for the case where the request body contains the validation error, otherwise the client will receive a generic, unhelpful error message.

### Use `AWS::Serverless::Api` in your CloudFormation template

`AWS::Serverless::Api` is a special resource type provided by [AWS SAM](https://aws.amazon.com/serverless/sam/), which simplifies configuration of API Gateway REST APIs when using AWS CloudFormation. When using `AWS::Serverless::Api`, there are additional best practices to note:

1. When authoring your own OpenAPI document, put it in a separate file and use the CloudFormation-provided `AWS::Include` transform to include it in the DefinitionBody property of the `AWS::Serverless::Api` resource. This has multiple advantages:
   1. It allows you to use CloudFormation intrinsic functions within your OpenAPI document, which is very useful for Amazon API Gateway extensions that require region and accountId information.
   1. Having your OpenAPI definition in its own file makes it easy to pass it to tools like swagger codegen to generate code from the definition.
   1. AWS SAM has some convenience features, such as adding CORS and authorizer support, where it needs access to make updates to your OpenAPI document during deployment. Normally, defining the OpenAPI document in a separate file means you can't use these SAM features. However, if you use `AWS::Include`, SAM will still be able to access to modify the OpenAPI definition at deployment time so these features are still available to you.
1. Explicitly set the OpenApiVersion property of `AWS::Serverless::Api` to the OpenAPI version you are using, even though it's already specified as part of the OpenAPI document. This is required to opt in to a [SAM bugfix](https://github.com/awslabs/serverless-application-model/issues/191#issuecomment-515589603).

**Examples in this project:**

1. [Using AWS::Serverless::Api](https://github.com/awslabs/realworld-serverless-application/blob/850ddf56764e59e1dd4ca2c40fd5bc8130061313/backend/sam/app/api.template.yaml#L29) to define a REST API.
1. OpenAPI document is [in a separate file](https://github.com/awslabs/realworld-serverless-application/blob/850ddf56764e59e1dd4ca2c40fd5bc8130061313/backend/swagger/api.yaml) and then [included into the template](https://github.com/awslabs/realworld-serverless-application/blob/850ddf56764e59e1dd4ca2c40fd5bc8130061313/backend/sam/app/api.template.yaml#L32-L36) using `AWS::Include`. Doing this allows the [use of CloudFormation intrinsic functions](https://github.com/awslabs/realworld-serverless-application/blob/850ddf56764e59e1dd4ca2c40fd5bc8130061313/backend/swagger/api.yaml#L78) within the OpenAPI document.
1. [Setting the OpenApiVersion property](https://github.com/awslabs/realworld-serverless-application/blob/850ddf56764e59e1dd4ca2c40fd5bc8130061313/backend/sam/app/api.template.yaml#L51) on `AWS::Serverless::Api`.

## Set API throttling limits

Set throttling limits on your REST API to prevent callers from abusing your service. One of the primary benefits of serverless is it can seamlessly scale to any volume and you only pay for what you use. However, if someone abuses your service and calls your API at a very high volume, this can drive your costs up. Prevent this by setting throttling limits on your API.

**Examples in this project:**

1. [Setting API throttling limits](https://github.com/awslabs/realworld-serverless-application/blob/850ddf56764e59e1dd4ca2c40fd5bc8130061313/backend/sam/app/api.template.yaml#L46-L47)

## Enable API logging

Amazon API Gateway supports two types of API logging in CloudWatch: execution logging and access logging.

### Execution Logging

Execution logging provides detailed logs for each API request. It can be enabled to log either at the INFO or ERROR level. In test environments, it's good to log at the INFO level for easier debugging. For very high volume APIs, the log level can be set to ERROR in production to reduce cost. API Gateway also has a setting to enable data trace, which logs request and response data to the execution log. This can be helpful in test environments for debugging, but should NOT be enabled in production environments to protect customer data.

### Access Logging

Access logging provides a single, highly structured log per request to the API. When used together with [CloudWatch Insights](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/AnalyzingLogData.html), this becomes a powerful way to quickly understand how your API is being used.

For more information on setting up logging in Amazon API Gateway, see the [Developer Guide](https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-logging.html).

**Examples in this project:**

1. Enabling logging first requires [creating an IAM role](https://github.com/awslabs/realworld-serverless-application/blob/850ddf56764e59e1dd4ca2c40fd5bc8130061313/backend/sam/app/api.template.yaml#L132-L145) that allows API Gateway to push logs to CloudWatch and [associating it with API Gateway](https://github.com/awslabs/realworld-serverless-application/blob/850ddf56764e59e1dd4ca2c40fd5bc8130061313/backend/sam/app/api.template.yaml#L146-L149).
1. [Enabling execution logging at the INFO level](https://github.com/awslabs/realworld-serverless-application/blob/850ddf56764e59e1dd4ca2c40fd5bc8130061313/backend/sam/app/api.template.yaml#L44) with [data trace only enabled in non-prod stages](https://github.com/awslabs/realworld-serverless-application/blob/850ddf56764e59e1dd4ca2c40fd5bc8130061313/backend/sam/app/api.template.yaml#L43).
1. Enabling access logging first requires [defining a log group for the access logs](https://github.com/awslabs/realworld-serverless-application/blob/850ddf56764e59e1dd4ca2c40fd5bc8130061313/backend/sam/app/api.template.yaml#L150-L154), then [enabling it on the API and defining the format of the log](https://github.com/awslabs/realworld-serverless-application/blob/850ddf56764e59e1dd4ca2c40fd5bc8130061313/backend/sam/app/api.template.yaml#L48-L50).

## Use Amazon API Gateway to generate client SDKs

Amazon API Gateway provides an API that will generate a client SDK for an Amazon API Gateway API. This is useful for generating client SDKs in different languages to publish to language-specific package repositories or to generate client SDKs used for integration tests against the API.

**Examples in this project:**

1. The backend integration tests use an Amazon API Gateway generated Java SDK to call the REST API. [A script](https://github.com/awslabs/realworld-serverless-application/blob/30a2cf044fb77c2ea0faf69d33a26281e2ab5480/bin/generate-sdk.sh) is run manually against a deployed instance of the backend service. The script uses the AWS CLI to [call Amazon API Gateway's get-sdk operation](https://github.com/awslabs/realworld-serverless-application/blob/30a2cf044fb77c2ea0faf69d33a26281e2ab5480/bin/generate-sdk.sh#L46-L50) on the deployed backend. The generated SDK client code is then committed to the repository as [test source code](https://github.com/awslabs/realworld-serverless-application/tree/30a2cf044fb77c2ea0faf69d33a26281e2ab5480/backend/src/test/java/software/amazon/serverless/apprepo/api/client).

## AWS Lambda

This application uses [AWS Lambda](https://aws.amazon.com/lambda/) for executing application logic. This page includes patterns and best practices for working with Lambda that are used in this application.

- [Use `AWS::Serverless::Function` to define Lambda functions in CloudFormation](#use-awsserverlessfunction-to-define-lambda-functions-in-cloudformation)
- [Configure async Lambda functions with a Dead-letter Queue (DLQ)](#configure-async-lambda-functions-with-a-dead-letter-queue-dlq)
- [Use a serverless API router library](#use-a-serverless-api-router-library)
- [Optimize the AWS Java SDK for better coldstart performance](#optimize-the-aws-java-sdk-for-better-coldstart-performance)

## Use `AWS::Serverless::Function` to define Lambda functions in CloudFormation

`AWS::Serverless::Function` is a special resource type provided by [AWS SAM](https://aws.amazon.com/serverless/sam/), which simplifies configuration of Lambda functions and related resources such as IAM roles, permissions, and event source mappings. When using `AWS::Serverless::Function`, there are additional best practices:

1. If your organization allows you to create your own IAM roles within your CloudFormation templates, use [SAM policy templates](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-policy-templates.html) to simplify Lambda function permissions while maintaining least privilege best practices.
1. For Lambda functions that will synchronously process API requests, enable [gradual code deployment](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/automating-updates-to-serverless-apps.html) via [AWS CodeDeploy](https://docs.aws.amazon.com/codedeploy/latest/userguide/welcome.html) in production with rollback triggers on API CloudWatch alarms. AWS SAM makes this configuration very simple.

**Examples in this project:**

1. [Using AWS::Serverless::Function](https://github.com/awslabs/realworld-serverless-application/blob/850ddf56764e59e1dd4ca2c40fd5bc8130061313/backend/sam/app/api.template.yaml#L75) to define the API Lambda function.
1. Simplifying Lambda function permissions using [SAM policy templates](https://github.com/awslabs/realworld-serverless-application/blob/850ddf56764e59e1dd4ca2c40fd5bc8130061313/backend/sam/app/api.template.yaml#L87-L90).
1. [Enabling gradual code deployment](https://github.com/awslabs/realworld-serverless-application/blob/850ddf56764e59e1dd4ca2c40fd5bc8130061313/backend/sam/app/api.template.yaml#L105-L113). Note, [a conditional is used](https://github.com/awslabs/realworld-serverless-application/blob/850ddf56764e59e1dd4ca2c40fd5bc8130061313/backend/sam/app/api.template.yaml#L109) so deployment is gradual in production, but fast in development and test environments. Gradual code deployment is configured to automatically fail the deployment and rollback if [configured API alarms](https://github.com/awslabs/realworld-serverless-application/blob/850ddf56764e59e1dd4ca2c40fd5bc8130061313/backend/sam/app/api.template.yaml#L156-L204) go into alarm state during the gradual code deployment.

## Configure async Lambda functions with a Dead-letter Queue (DLQ)

Async Lambda functions are frequently used to process events from various sources, e.g., DynamoDB streams and SQS queues. In the event the Lambda function throws an error attempting to process an event, the Lambda service will retry the request a few times. If the failure continues, Lambda's default behavior is to drop the event. However, if you configure a dead-letter queue (DLQ) for the Lambda function, Lambda will write the failed event to the DLQ. In a production system, it's critical to configure all async processing Lambda functions with a DLQ to ensure events are not dropped and can instead be debugged and redriven. Here are some best practices for working with Lambda DLQs.

1. Prefer Amazon SQS to Amazon SNS for Lambda DLQs. SQS can hold messages for up to 14 days and works well for automating message replay.
1. Events should be written to the DLQ in the same format that the async processing Lambda function expects. This allows events on the DLQ to be redriven directly through the same async processing Lambda function rather than having to write some custom business logic for processing DLQ events.
1. If a Lambda function is already being triggered from an SQS queue, configure the SQS DLQ on the SQS queue directly instead of on the Lambda function. Both Lambda and SQS provide DLQ features. We prefer to use the SQS DLQ feature when it's available since it gives more control over the number of retries and ensures the event stored in the DLQ is in the same format as the event stored in the source SQS queue for easier redrive.
1. For stream-based Lambda functions, unless strict write ordering is critical to your application, e.g., you're replicating a DynamoDB table to another DynamoDB table, use an event fanout solution that supports DLQ. This is because Lambda does not natively support writing failed events to a DLQ for stream-based Lambda functions, which can cause stream processing to get blocked if the Lambda function cannot process an event in the stream. For example, this application uses an app to fanout DynamoDB stream events to [Amazon EventBridge](https://aws.amazon.com/eventbridge/).

**Examples in this project:**

1. The [aws-dynamodb-stream-eventbridge-fanout](https://github.com/awslabs/aws-dynamodb-stream-eventbridge-fanout) serverless app is [nested in the analytics stack](https://github.com/awslabs/realworld-serverless-application/blob/6b98360059490878f5ec43083dc27b09e096952e/analytics/sam/app/template.yaml#L27-L34) and configured to attach to the Applications table's DynamoDB stream in order to forward the stream events to Amazon EventBridge. This allows multiple Lambda functions to process stream events since there's a limit of how many Lambda functions can be attached directly to a DynamoDB stream without being throttled. The fanout app writes events to [an SQS DLQ](https://github.com/awslabs/aws-dynamodb-stream-eventbridge-fanout/blob/a9b8e8adabc4000d4df240b3ea38ffda0d5eb782/sam/app/template.yaml#L66-L67) if they cannot be written successfully to Amazon EventBridge. The DLQ is [available as an output](https://github.com/awslabs/aws-dynamodb-stream-eventbridge-fanout/blob/a9b8e8adabc4000d4df240b3ea38ffda0d5eb782/sam/app/template.yaml#L73-L75) of the app for alarming or redriving purposes.

## Use a serverless API router library

For Lambda functions that service API requests from Amazon API Gateway, we've found it best to use a library to automatically route API requests to the right handler method within your Lambda function code. Popular examples of serverless API router libraries are [aws-serverless-java-container](https://github.com/awslabs/aws-serverless-java-container) (Java) and [aws-serverless-express](https://github.com/awslabs/aws-serverless-express) (Node.js).

Whether all API operations should be handled by a single Lambda function or separate Lambda functions is still a heated topic within the serverless community. However, we've found using an API router library gives you the flexibility to choose either option or something in between, without having to change your Lambda function code.

**Examples in this project:**

1. This project uses [aws-serverless-java-container for Jersey](https://github.com/awslabs/realworld-serverless-application/blob/850ddf56764e59e1dd4ca2c40fd5bc8130061313/backend/pom.xml#L111). Jersey is an implementation of JAX-RS, the Java API for RESTful Web Services.
1. The [swagger-codegen-maven-plugin](https://github.com/awslabs/realworld-serverless-application/blob/850ddf56764e59e1dd4ca2c40fd5bc8130061313/backend/pom.xml#L441) is configured to generate API model classes based on the [OpenAPI API definition](https://github.com/awslabs/realworld-serverless-application/blob/850ddf56764e59e1dd4ca2c40fd5bc8130061313/backend/pom.xml#L451). At build time, this generates Java classes for all API request and response objects as well as a JAX-RS annotated Java interface for the API itself.
1. The [ApplicationService class](https://github.com/awslabs/realworld-serverless-application/blob/850ddf56764e59e1dd4ca2c40fd5bc8130061313/backend/src/main/java/software/amazon/serverless/apprepo/api/impl/ApplicationsService.java#L55) implements the generated interface and supplies the business logic of each API operation. For example, it provides the business logic of the [CreateApplication operation](https://github.com/awslabs/realworld-serverless-application/blob/850ddf56764e59e1dd4ca2c40fd5bc8130061313/backend/src/main/java/software/amazon/serverless/apprepo/api/impl/ApplicationsService.java#L104).
1. Within the Lambda handler class for the API Lambda function, [the Jersey application is configured](https://github.com/awslabs/realworld-serverless-application/blob/850ddf56764e59e1dd4ca2c40fd5bc8130061313/backend/src/main/java/software/amazon/serverless/apprepo/container/ApiLambdaHandler.java#L38-L56) and passed to a [JerseyLambdaContainerHandler handler instance](https://github.com/awslabs/realworld-serverless-application/blob/850ddf56764e59e1dd4ca2c40fd5bc8130061313/backend/src/main/java/software/amazon/serverless/apprepo/container/ApiLambdaHandler.java#L58-L59) provided by the aws-serverless-java-container library. All Lambda requests are [passed to the handler](https://github.com/awslabs/realworld-serverless-application/blob/850ddf56764e59e1dd4ca2c40fd5bc8130061313/backend/src/main/java/software/amazon/serverless/apprepo/container/ApiLambdaHandler.java#L64), which routes the request to the right method in the ApplicationsService class.

## Optimize the AWS Java SDK for better coldstart performance

Use best practices around configuring the AWS Java SDK for use in Lambda environments:

1. Use the AWS Java SDKv2 with [suggested optimizations for Lambda](https://docs.aws.amazon.com/sdk-for-java/v2/developer-guide/client-configuration-starttime.html).
1. Add dependencies on only the specific service clients needed for the project to minimize overall size of the Lambda binary.
1. Customize SDK timeout and retry configuration for your application. The default SDK timeout and retry values may not make sense for the AWS service being called or the constraints of the backend service environment. In the worst case, the default settings can result in high latencies and/or availability risks to the backend service.

**Examples in this project:**

1. Adding dependencies on the minimum AWS Java SDKv2 components needed by the backend: [url-connection-client](https://github.com/awslabs/realworld-serverless-application/blob/850ddf56764e59e1dd4ca2c40fd5bc8130061313/backend/pom.xml#L71), [DynamoDB](https://github.com/awslabs/realworld-serverless-application/blob/850ddf56764e59e1dd4ca2c40fd5bc8130061313/backend/pom.xml#L126), and [KMS](https://github.com/awslabs/realworld-serverless-application/blob/850ddf56764e59e1dd4ca2c40fd5bc8130061313/backend/pom.xml#L131).
1. Following [suggested SDK configuration](https://github.com/awslabs/realworld-serverless-application/blob/850ddf56764e59e1dd4ca2c40fd5bc8130061313/backend/src/main/java/software/amazon/serverless/apprepo/container/factory/DynamoDbClientFactory.java#L20-L29) for Lambda environments.
1. [Customizing timeout and retry policy](https://github.com/awslabs/realworld-serverless-application/blob/850ddf56764e59e1dd4ca2c40fd5bc8130061313/backend/src/main/java/software/amazon/serverless/apprepo/container/factory/DynamoDbClientFactory.java#L26-L27) for DynamoDB client. Rationale: DynamoDB requests should normally have single digit millisecond response times so allow many retries, but cap the total request duration at 1 second to ensure API latency doesn't get out of control if the service is taking longer than usual to respond.


## DevOps

This application uses [Amazon CloudWatch](https://aws.amazon.com/cloudwatch/) for managing operations (DevOps). This page includes patterns and best practices for working with CloudWatch that are used in this application.

- [Setup operations infrastructure in a separate stack](#setup-operations-infrastructure-in-a-separate-stack)
- [Alarming on API metrics vs Lambda metrics](#alarming-on-api-metrics-vs-lambda-metrics)
- [Configure dashboards via the AWS CloudWatch console](#configure-dashboards-via-the-aws-cloudwatch-console)
- [Add CloudWatch Insights queries on API access logs to dashboards](#add-cloudwatch-insights-queries-on-api-access-logs-to-dashboards)

## Setup operations infrastructure in a separate stack

Operations infrastructure like alarms and dashboards are setup in a separate stack from the primary backend service infrastructure. This keeps deployment of operations infrastructure decoupled from deployment of the actual backend service. This is useful because generally you will want to deploy changes to alarms and dashboards quickly compared to deployment of the actual production service. It also helps you avoid hitting CloudFormation stack resource limits since a complex service can have many alarms.

In this application, the ops stack is broken up into 2 nested stacks: one for alarms and one for dashboards. However, note in a more complex service, you may choose to organize alarms into multiple nested stacks, e.g., alarms for synchronous API request processing vs alarms for async stream processing.

**Examples in this project:**

1. Operations infrastructure is created as part of a [separate ops stack](https://github.com/awslabs/realworld-serverless-application/blob/6b98360059490878f5ec43083dc27b09e096952e/ops/sam/app/template.yaml), which [contains nested stacks for alarms and dashboards](https://github.com/awslabs/realworld-serverless-application/blob/6b98360059490878f5ec43083dc27b09e096952e/ops/sam/app/template.yaml#L27-L38).

## Alarming on API metrics vs Lambda metrics

For Lambda functions that handle synchronous API requests, it's better to add alarming on error and latency metrics produced by Amazon API Gateway rather than metrics produced by AWS Lambda. Amazon API Gateway metrics are more granular, providing per-operation metrics as well as splitting error metrics into 4xx (client errors) and 5xx (service errors), which is useful for differentiating when a service bug caused an issue vs a normal client error such as an input validation error. The latency metrics provided by Amazon API Gateway are also closer to what the client is actually experiencing since it includes the overhead of Amazon API Gateway processing the request in addition to Lambda.

For asynchronous Lambda functions, e.g., those triggered by an S3 bucket write or an SQS queue, assuming you're following the best practice of [configuring a DLQ on all async processing Lambda functions](https://github.com/awslabs/realworld-serverless-application/wiki/AWS-Lambda#configure-async-lambda-functions-with-a-dead-letter-queue-dlq), you should alarm on DLQ message counts (SQS `ApproximateNumberOfMessagesVisible` metric) rather than Lambda function errors. This is because the Lambda service will automatically retry failed async Lambda requests. If you configure your alarm on Lambda function errors, it could give you false alarms when functions encounter transient errors but then succeed on retry.

**Examples in this project:**

1. [Configuring API alarms against Amazon API Gateway metrics](https://github.com/awslabs/realworld-serverless-application/blob/6b98360059490878f5ec43083dc27b09e096952e/ops/sam/app/alarm.template.yaml#L26-L97) rather than Lambda metrics.

## Configure dashboards via the AWS CloudWatch console

CloudWatch dashboards are a powerful way to get a quick view of the health of your system. They should be managed by AWS CloudFormation so they are deployed along with the rest of your application. However, writing a dashboard configuration in CloudFormation by hand is extremely painful. A nice shortcut is to use the AWS CloudWatch console to manually configure your dashboard. Then you can click on Actions -> View/edit source. This will give you the JSON definition of the dashboard, which you can copy/paste into your CloudFormation template. You should then use `Fn::Sub` to replace any hardcoded values within the dashboard definition with template references to ensure the template is portable.

**Examples in this project:**

1. [Dashboard definition](https://github.com/awslabs/realworld-serverless-application/blob/6b98360059490878f5ec43083dc27b09e096952e/ops/sam/app/dashboard.template.yaml#L29) was originally pasted from the CloudWatch console, but note references like [AWS region](https://github.com/awslabs/realworld-serverless-application/blob/6b98360059490878f5ec43083dc27b09e096952e/ops/sam/app/dashboard.template.yaml#L46) and [Lambda function names](https://github.com/awslabs/realworld-serverless-application/blob/6b98360059490878f5ec43083dc27b09e096952e/ops/sam/app/dashboard.template.yaml#L44) have been replaced with CloudFormation references.

## Add CloudWatch Insights queries on API access logs to dashboards

CloudWatch Insights combined with Amazon API Gateway access logging are a powerful combination for quickly understanding the requests coming into your service. They can be used to quickly query top users for a given time period or in an outage scenario, top users impacted by the outage. The dashboard also links you to the CloudWatch insights console, allowing you to modify the query and run it ad hoc which is useful during outage situations.

**Examples in this project:**

1. The dashboard defined in the ops stack includes several CloudWatch Insights queries that are useful in real world applications, e.g., [Top 10 Customers Impacted by API 5xx errors](https://github.com/awslabs/realworld-serverless-application/blob/6b98360059490878f5ec43083dc27b09e096952e/ops/sam/app/dashboard.template.yaml#L286-L301).
