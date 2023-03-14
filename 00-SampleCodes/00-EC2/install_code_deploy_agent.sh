#!/bin/bash
REGION=$(curl 169.254.169.254/latest/meta-data/placement/availability-zone/ | sed 's/[a-z]$//')
yum -y update
yum install ruby wget -y
cd /home/ec2-user
wget https://aws-codedeploy-$REGION.s3.amazonaws.com/latest/install
chmod +x ./install
./install auto
service codedeploy-agent stop
sed -i 's,'/opt/codedeploy-agent/deployment-root','/tmp',g' /etc/codedeploy-agent/conf/codedeployagent.yml
service codedeploy-agent start