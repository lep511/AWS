INSTANCE_EC2=$(aws ec2 describe-instances --filter "Name=tag:Name,Values=hi-avail-cdk/PrivateInstance" --query "Reservations[].Instances[?State.Name == 'running'].InstanceId[]" --output text)
aws ssm start-session --target $INSTANCE_EC2
