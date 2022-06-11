Run the template.  Pass in 3 parameters:
•	DBInstanceMasterPassword
•	PhotoBucketName – give a unique bucket name to store the photos
•	StaticBucketName – give a unique bucket name to store the application zip

The template creates:
•	VPC, Subnets, IGW
•	RDS database, subnet group, security group
•	Dynamo table: Employees
•	Instance-role
•	Check the output for a link to the zip we build, it will look like this: https://emp3-application.s3.amazonaws.com/corp-app.zip


Create the RDS app
==================

Create an ec2 instance:
•	VPC: app-vpc
•	Subnet: any public
•	User-data

#!/bin/bash -ex
wget [insert the CF output zip here]
unzip corp-app.zip
./install_launch.sh

•	Security group: 	web-security-group


Create the Dynamo app
=====================

Create an ec2 instance:
•	VPC: default vpc okay
•	Subnet: any public
•	User-data

#!/bin/bash -ex
wget [insert the CF output zip here]
unzip corp-app.zip
./install_launch_dynamo.sh

•	Security group: 	web-security-group



Creating the zip
=========



git archive --format=zip -o ~/corp-app.zip HEAD
# put the zip somewhere public
aws s3 cp ~/corp-app.zip s3://us-west-2-tcdev/labs/ --profile awsu
