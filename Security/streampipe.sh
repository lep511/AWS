!#/bin/bash
# This script is for installing steampipe and aws cli
# https://steampipe.io/blog/cis-v30-aws-benchmark
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

echo "run aws configure in another terminal"
pasue

sudo /bin/sh -c "$(curl -fsSL https://steampipe.io/install/steampipe.sh)"
steampipe -v
steampipe plugin install steampipe
steampipe plugin install aws
git clone https://github.com/turbot/steampipe-mod-aws-compliance.git
cd steampipe-mod-aws-compliance
steampipe check aws_compliance.benchmark.cis_v300

steampipe dashboard