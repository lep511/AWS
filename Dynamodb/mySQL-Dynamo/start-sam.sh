#!/bin/bash

read -p "Create key-pair for EC2 (y/N): " createkey

if [[ "$createkey" =~ ^([yY][eE][sS]|[yY])$ ]]
then
    read -p 'Enter key-pair name: ' keyname

    aws ec2 create-key-pair \
        --key-name $keyname \
        --key-type rsa \
        --key-format pem \
        --query "KeyMaterial" \
        --output text > $keyname.pem

    chmod 400 $keyname.pem

    sam build
    sam deploy -g --parameter-overrides DBKeyName=$keyname --capabilities CAPABILITY_NAMED_IAM
else
    sam build
    sam deploy -g --capabilities CAPABILITY_NAMED_IAM
fi

