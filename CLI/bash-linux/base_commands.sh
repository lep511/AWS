#!/bin/bash

sudo su - ec2-user

ls -ltr

more stage_files.sh

INPUT_BUCKET=$(aws s3 ls | grep "lab-materials-" | awk '{print $3}')

ACCOUNT=`aws sts get-caller-identity | jq .Account | sed 's/"//g'`

REGION=`curl --silent http://169.254.169.254/latest/dynamic/instance-identity/document | jq '.region' | sed 's/"//g'`

LATEST=':latest'

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com

for i in `ls *.tar.gz`
        do
                IMAGE_ID=`echo $i | cut -d "-" -f1`
                REPO_NAME=`echo $i | cut -d "-" -f2 | cut -d "." -f1`
                echo "Begin push of Image $IMAGE_ID to ECR Repo $REPO_NAME"
                docker load < $i
                docker tag $IMAGE_ID ${REPO_NAME}${LATEST}
                docker tag  ${REPO_NAME}${LATEST} ${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com/${REPO_NAME}${LATEST}
                docker push ${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com/${REPO_NAME}${LATEST}
        done;
exit 0