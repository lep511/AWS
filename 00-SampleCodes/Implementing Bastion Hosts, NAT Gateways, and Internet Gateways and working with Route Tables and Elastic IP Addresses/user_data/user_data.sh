#!/bin/bash
sudo yum update -y
sudo yum -y install httpd php
sudo chkconfig httpd on
sudo service httpd start
sudo touch metadata.sh
sudo chmod 777 metadata.sh
sudo echo 'curl http://169.254.169.254/latest/meta-data/$1' > metadata.sh
sudo echo 'VAR=' >> metadata.sh
sudo echo 'echo $VAR' >> metadata.sh