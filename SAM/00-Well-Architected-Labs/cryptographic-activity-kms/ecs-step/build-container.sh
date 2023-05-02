#!/bin/bash

BASE_STACK=$1
ECR_REPONAME=$(aws cloudformation describe-stacks --stack-name $BASE_STACK --query 'Stacks[0].Outputs[?OutputKey==`OutputPattern1AppContainerRepository`].OutputValue |[0]' | sed 's/"//g')
STACK_ID=$(aws cloudformation describe-stacks --stack-name $BASE_STACK --query 'Stacks[0].StackId' | sed 's/"//g')

echo $ECR_REPONAME


IFS=':'
read -ra ADDR <<< "$STACK_ID" # str is read into an array as tokens separated by IFS

AWS_REGION=${ADDR[3]}
AWS_ACCOUNT=${ADDR[4]}
echo "Image URI:" $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPONAME:latest

aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com
docker build -t $ECR_REPONAME .
docker tag $ECR_REPONAME:latest $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPONAME:latest
docker push $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPONAME:latest


echo "==========================="
echo "Image URI:" $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPONAME:latest

