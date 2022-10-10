#!/bin/bash
# exit when any command fails
set -e
script_path=$(cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P)
sam deploy --template-file ${script_path}/../template.yaml --stack-name my-microservice --capabilities CAPABILITY_IAM --guided