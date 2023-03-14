#!/bin/bash
sudo yum update -y
sudo yum -y install jq
sudo yum install -y python3
cd /home/ec2-user

aws s3 cp s3://pu-base-buckets-v1-provision-lab/10feff16-6cd5-4be5-b52d-c24e5639c68e/pdar_app.zip /home/ec2-user/
unzip pdar_app.zip
pip3 install -r requirements.txt

export AWS_DEFAULT_REGION=$(curl -s http://169.254.169.254/latest/dynamic/instance-identity/document|jq -r .region)
export EC2_INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)

echo instance_id=$EC2_INSTANCE_ID >> .env
echo REGION=$AWS_DEFAULT_REGION >> .env
python3 app.py