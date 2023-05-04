#!/bin/bash
# Deploy the SAM stack
sam build
sam deploy

# Deploy the second stack
sam build --template-file cloudfront-cognito.yaml
sam deploy --template-file cloudfront-cognito.yaml --config-file cloudfront-cognito.toml --guided