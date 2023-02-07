""" 
Make sure you install all of the aws packages listed in the import statement 
by running pip install commands following this pattern:
pip install aws_cdk.aws_<service name> 
where <service name> is the name of each package, such as ec2
"""

from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    core,
)

class HiAvailCdkStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # create VPC w/ public and private subnets in 2 AZs
        #     this also creates NAT Gateways in our public subnets
        vpc = ec2.Vpc(
            self, "MyVpc",
            max_azs=2
        )

        # define the IAM role that will allow the EC2 instance to communicate with SSM
        role = iam.Role(self, "Role", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))
        # arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore
        role.add_managed_policy(iam.ManagedPolicy(self, id='mp', managed_policy_name='AmazonSSMManagedInstanceCore', statements=[iam.PolicyStatement(actions=['*'], resources=['*'])]))
        # define user data script to update server software
        ssma_user_data = ec2.UserData.for_linux()
        ssma_user_data.add_commands('sudo yum update -y')
        # define user data script to create metadata.sh script
        ssma_user_data.add_commands('sudo touch metadata.sh')
        ssma_user_data.add_commands('sudo chmod 777 metadata.sh')
        ssma_user_data.add_commands("sudo echo 'curl http://169.254.169.254/latest/meta-data/$1' > metadata.sh")
        ssma_user_data.add_commands("sudo echo 'VAR=' >> metadata.sh")
        ssma_user_data.add_commands("sudo echo 'echo $VAR' >> metadata.sh")


        # launch an EC2 instance in the private subnet
        instance = ec2.Instance(
            self, "PrivateInstance",
            vpc=vpc,
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO
            ),
            machine_image=ec2.AmazonLinuxImage(),
            vpc_subnets={ 'subnet_type': ec2.SubnetType.PRIVATE },
            role=role,
            user_data=ssma_user_data
        )
