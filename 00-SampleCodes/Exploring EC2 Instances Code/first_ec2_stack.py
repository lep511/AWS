""" 
Make sure you install all of the aws packages listed in the import statement 
by running pip install commands following this pattern:
pip install aws_cdk.aws_<service name> 
where <service name> is the name of each package, such as ec2
"""

from aws_cdk import (
    aws_ec2 as ec2,
    core
)

class FirstEc2Stack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here
        vpc = ec2.Vpc(
            self, "MyVpc",
            max_azs=1
        )

        sg = ec2.SecurityGroup(
            self, "SG",
            description='Allow ssh access to ec2 instances',
            vpc=vpc
        )

        sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(22)
        )

        ec2instance = ec2.Instance(
            self, "EC2INSTANCE",
            vpc=vpc,
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO
            ),
            machine_image=ec2.AmazonLinuxImage(),
            vpc_subnets={'subnet_type': ec2.SubnetType.PUBLIC},
            security_group=sg,
            key_name="MyNVKeyPair"
        )
