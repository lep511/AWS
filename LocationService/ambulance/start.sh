#!/usr/bin/env bash
# stop script on error
set -e

# Check for python 3
if ! python3 --version &> /dev/null; then
  printf "\nERROR: python3 must be installed.\n"
  exit 1
fi

# Check to see if root CA file exists, download if not
if [ ! -f ./root-CA.crt ]; then
  printf "\nDownloading AWS IoT Root CA certificate from AWS...\n"
  curl https://www.amazontrust.com/repository/AmazonRootCA1.pem > root-CA.crt
fi

# Check to see if AWS Device SDK for Python exists, download if not
if [ ! -d ./aws-iot-device-sdk-python-v2 ]; then
  printf "\nCloning the AWS SDK...\n"
  git clone https://github.com/aws/aws-iot-device-sdk-python-v2.git --recursive
fi

# Check to see if AWS Device SDK for Python is already installed, install if not
if ! python3 -c "import awsiot" &> /dev/null; then
  printf "\nInstalling AWS SDK...\n"
  python3 -m pip install ./aws-iot-device-sdk-python-v2
  result=$?
  if [ $result -ne 0 ]; then
    printf "\nERROR: Failed to install SDK.\n"
    exit $result
  fi
fi

# Check to see if AWS Boto is already installed, install if not
if ! python3 -c "import boto3" &> /dev/null; then
  printf "\nInstalling AWS boto3...\n"
  python3 -m pip install boto3
  result=$?
  if [ $result -ne 0 ]; then
    printf "\nERROR: Failed to install boto3.\n"
    exit $result
  fi
fi

# The above code just needs to be executed once during
# the practice section to setup the Cloud9 enviornment.

# Use boto to get the lab account IoT Endpoint
export ENDPOINT=`aws --region us-east-1 iot describe-endpoint --endpoint-type iot:Data-ATS --output text`

# Set the variables to the certificate and private key. 
export PATH_TO_CERTIFICATE=`ls *certificate.pem.crt`
export PATH_TO_PRIVATE_KEY=`ls *private.pem.key`

# Run the ambulance data generator script.
# For the DIY you will not use this start script.
printf "\nRunning send_ambulance_data.py data generator...\n"
python3 send_ambulance_data.py
