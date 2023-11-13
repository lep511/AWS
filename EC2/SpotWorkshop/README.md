## SAM Template for Spot Workshops

This template creates a VPC with 6 public subnets, an Application Load Balancer, an Auto Scaling Group with a Launch Template that uses Spot Instances, and a Target Group.

`sam build`<br>
`sam deploy -g --capabilities CAPABILITY_IAM`