# OpenAI GPT-3 API with AWS Step Functions

This pattern demonstrates how to use the OpenAI GPT-3 API with AWS Step Functions.

Learn more about this pattern at Serverless Land Patterns: https://serverlessland.com/patterns/

## Deployment Instructions

1. Build the SAM application:
    ``` 
    sam build
    ```

2. From the command line, use AWS SAM to deploy the AWS resources for the pattern as specified in the template.yml file:
    ```
    sam deploy -g --capabilities CAPABILITY_NAMED_IAM CAPABILITY_IAM
    ```
3. During the prompts:
    * Enter a stack name
    * Select the desired AWS Region
    * Enter the OpenAI API key

    Once you have run guided mode once, you can use `sam deploy` in future to use these defaults.

4. Note the outputs from the SAM deployment process. These contain the resource names and/or ARNs which are used for testing.

## Cleanup
 
1. Delete the stack
    ```bash
    sam delete
    ```
----