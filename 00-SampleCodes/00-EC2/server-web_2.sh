#!/bin/sh
yum -y install httpd php
chkconfig httpd on
systemctl start httpd.service
cd /var/www/html
wget https://us-west-2-aws-training.s3.amazonaws.com/courses/spl-03/v4.3.15.prod-0f2a1e18/scripts/examplefiles-elb.zip
unzip examplefiles-elb.zip