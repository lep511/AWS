## Serverless XGBoost Model Serving on Graviton2 architecture

This examples illustrates how to serve XGBoost model on Lambda Function on Graviton2 architecture to predict breast cancer.

In addition, there is a code sample to help you compare performance of the XGBoost x86_64 Lambda Function with Arm64 (Graviton2) one.

This project contains source code and supporting files for a serverless application that you can deploy with the SAM CLI. It includes the following files and folders.

- app - Code for the application's Lambda function.
- train-code - Code for training XGBoost model based on breast cancer dataset.
- events - Invocation events that you can use to invoke the function.
- template.yaml - A template that defines the application's AWS resources.
- invoke_x86_64_arm64_lambdas.py - Code to invoke x86_64 and Arm64 (Graviton2) Lambda Functions and compare performance.  

The application uses several AWS resources, including Lambda functions. These resources are defined in the `template.yaml` file in this project. You can update the template to add AWS resources through the same deployment process that updates your application code.

## Deploy the sample application

The Serverless Application Model Command Line Interface (SAM CLI) is an extension of the AWS CLI that adds functionality for building and testing Lambda applications. It uses Docker to run your functions in an Amazon Linux environment that matches Lambda. It can also emulate your application's build environment and API.

To use the SAM CLI, you need the following tools.

* SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* Docker - [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)

You may need the following for local testing.
* [Python 3 installed](https://www.python.org/downloads/)

To build and deploy your application for the first time, run the following in your shell:

```bash
sam build
sam deploy --guided
```

The first command will build a docker image from a Dockerfile and then copy the source of your application inside the Docker image. The second command will package and deploy your application to AWS, with a series of prompts:

* **Stack Name**: The name of the stack to deploy to CloudFormation. This should be unique to your account and region, and a good starting point would be something matching your project name.
* **AWS Region**: The AWS region you want to deploy your app to.
* **Confirm changes before deploy**: If set to yes, any change sets will be shown to you before execution for manual review. If set to no, the AWS SAM CLI will automatically deploy application changes.
* **Allow SAM CLI IAM role creation**: Many AWS SAM templates, including this example, create AWS IAM roles required for the AWS Lambda function(s) included to access AWS services. By default, these are scoped down to minimum required permissions. To deploy an AWS CloudFormation stack which creates or modified IAM roles, the `CAPABILITY_IAM` value for `capabilities` must be provided. If permission isn't provided through this prompt, to deploy this example you must explicitly pass `--capabilities CAPABILITY_IAM` to the `sam deploy` command.
* **Save arguments to samconfig.toml**: If set to yes, your choices will be saved to a configuration file inside the project, so that in the future you can just re-run `sam deploy` without parameters to deploy changes to your application.

## Use the SAM CLI to build and test locally

Build your application with the `sam build` command.

```bash
xgboost-inference-arm64-docker-lambda$ sam build
```

The SAM CLI builds a docker image from a Dockerfile and then installs dependencies defined in `requirements.txt` inside the docker image. The processed template file is saved in the `.aws-sam/build` folder.

Test a single function by invoking it directly with a test event. An event is a JSON document that represents the input that the function receives from the event source. Test events are included in the `events` folder in this project.

Run functions locally and invoke them with the `sam local invoke` command.

```bash
xgboost-inference-arm64-docker-lambda$ sam local invoke XGBoostInferenceArm64Function --event events/event.json
```

## View your Lambda Architecture

1. In the [Lambda Console](https://console.aws.amazon.com/lambda/), select the `Image` tab and scrll down to the `Image` section.
2. For `Architecture` you should see `arm64`

![arm64 Architecture](../img/xgboost_arm_64_arch_view.png)

## Compare performance of x86_64 Lambda Function with Arm64 (Graviton2) one

You can achieve up to 34% better price/performance with AWS Lambda Functions powered by AWS Graviton2 processor.

To test the performance improvements of the XGBoost x86_64 Lambda Function with an Arm64 (Graviton2) one yourself, please execute the following steps:
1. Deploy the XGBoost x86_64 Lambda Function, as described [here](../xgboost-inference-docker-lambda/)
2. Open `invoke_x86_64_arm64_lambdas.py` file.
3. Replace `<XGBoost_x86_64_Lambda_ARN>` with XGBoost x86_64 Lambda Function ARN.
4. Replace `<XGBoost_arm64_Lambda_ARN>` with XGBoost Arm64 (Graviton2) Lambda Function ARN.
5. Run the following command: `python invoke_x86_64_arm64_lambdas.py`

![xgboost x86_64 vs. arm64 improvement](../img/xgboost_x86_64_arm64_improvement.png)

**We can see that the Arm64 (Graviton2) Lambda Function has performance improvements of 36% over the x86_64 one!**

## Testing your Lambda function in the Cloud

1. In the [Lambda Console](https://console.aws.amazon.com/lambda/), select Configure test events from the Test events dropdown.
2. For Event Name, enter InferenceTestEvent.
3. Copy the event JSON from [here](./events/event.json) and paste in the dialog box.
4. Choose _**Create**_.

![Configure test event](../img/xgboost_configure_test_event.png)

After saving, you see InferenceTestEvent in the Test list. Now choose _**Test**_.

You see the Lambda function inference result, log output, and duration:

![Lambda execution result](../img/xgboost_arm_64_execution_result.png)

## Fetch, tail, and filter Lambda function logs

To simplify troubleshooting, SAM CLI has a command called `sam logs`. `sam logs` lets you fetch logs generated by your deployed Lambda function from the command line. In addition to printing the logs on the terminal, this command has several nifty features to help you quickly find the bug.

`NOTE`: This command works for all AWS Lambda functions; not just the ones you deploy using SAM.

```bash
xgboost-inference-arm64-docker-lambda$ sam logs -n XGBoostInferenceArm64Function --stack-name xgboost-inference-arm64-docker-lambda --tail
```

You can find more information and examples about filtering Lambda function logs in the [SAM CLI Documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-logging.html).

## Cleanup

To delete the sample application that you created, use the AWS CLI. Assuming you used your project name for the stack name, you can run the following:

```bash
aws cloudformation delete-stack --stack-name xgboost-inference-arm64-docker-lambda
```

## Resources

See the [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) for an introduction to SAM specification, the SAM CLI, and serverless application concepts.

