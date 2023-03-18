#!/bin/bash

## UPDATE ENV VAR LAMBDA
export apiId=`aws apigateway get-rest-apis --query 'items[*].id' --output text`
aws lambda update-function-configuration --function-name producer-app-1 --environment Variables={restapiId=$apiId}
aws lambda update-function-configuration --function-name producer-app-2 --environment Variables={restapiId=$apiId}

## Invoke Lambda 1
aws lambda invoke --function-name producer-app-1 --invocation-type Event response.json

## Wait 3 minutes to stress the app
sleep 180
for i in {1..3}; 
do
    aws lambda invoke --function-name producer-app-2 --invocation-type Event response.json
done
