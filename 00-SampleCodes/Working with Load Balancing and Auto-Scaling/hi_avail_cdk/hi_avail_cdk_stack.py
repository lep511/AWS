""" 
Make sure you install all of the aws packages listed in the import statement 
by running pip install commands following this pattern:
pip install aws_cdk.aws_<service name> 
where <service name> is the name of each package, such as ec2
"""

from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_elasticloadbalancingv2 as elb,
    aws_autoscaling as autoscaling,
    aws_rds as rds,
    core,
)


# define EC2 type
ec2_type = "t2.micro"
linux_ami=ec2.AmazonLinuxImage()

# read in userData, used to install httpd and start the httpd service on web EC2 instances
with open("./user_data/user_data.sh") as f:
    user_data = f.read()

class HiAvailCdkStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, *, stack_tag="default", **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

     # define the vpc with 3 subnets across 2 AZs
        vpc = ec2.Vpc(self, stack_tag,
                           max_azs=2,
                           cidr="10.10.0.0/16",
                           # configuration will create 3 groups in 2 AZs = 6 subnets.
                           subnet_configuration=[ec2.SubnetConfiguration(
                               subnet_type=ec2.SubnetType.PUBLIC,
                               name="Public",
                               cidr_mask=24
                           ), ec2.SubnetConfiguration(
                               subnet_type=ec2.SubnetType.PRIVATE,
                               name="Private",
                               cidr_mask=24
                           ), ec2.SubnetConfiguration(
                               subnet_type=ec2.SubnetType.ISOLATED,
                               name="DB",
                               cidr_mask=24
                           )
                           ],
                           # nat_gateway_provider=ec2.NatProvider.gateway(),
                           nat_gateways=2,
                           )
    # define the IAM role that will allow the EC2 instance to communicate with SSM
        role = iam.Role(self, "Role", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))
        # arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore
        role_id="mp" + stack_tag
        policy_name="AmazonSSMManagedInstanceCore" + stack_tag
        role.add_managed_policy(iam.ManagedPolicy(self, id=role_id, managed_policy_name=policy_name,
                                                  statements=[iam.PolicyStatement(actions=['*'], resources=['*'])]))

        # Create ALB in our VPC. Set internet_facing to 'true'
        # to create an external application load balancer.
        alb = elb.ApplicationLoadBalancer(self, "myALB",
                                          vpc=vpc,
                                          internet_facing=True,
                                          load_balancer_name="myALB"
                                          )
        # allow internet access to port 80
        alb.connections.allow_from_any_ipv4(
            ec2.Port.tcp(80), "Internet access ALB via port 80")
        # listen on port 80
        listener = alb.add_listener("my80",
                                    port=80,
                                    open=True)

        asg = autoscaling.AutoScalingGroup(self, "myASG",
                                                vpc=vpc,
                                                vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE),
                                                instance_type=ec2.InstanceType(instance_type_identifier=ec2_type),
                                                machine_image=linux_ami,
                                                role=role,
                                                user_data=ec2.UserData.custom(user_data),
                                                desired_capacity=2,
                                                min_capacity=2,
                                                max_capacity=3,
                                                )

        asg.connections.allow_from(alb, ec2.Port.tcp(80), "ALB access port 80 of EC2 in Autoscaling Group")
        listener.add_targets("addTargetGroup",
                             port=80,
                             targets=[asg])

        # Scale to keep the CPU usage of your instances at around 50% utilization
        asg.scale_on_cpu_utilization("KeepSpareCPU",
                                     target_utilization_percent=50
                                     )

        # create MySQL RDS with CDK High Level API
        asg_security_groups=asg.connections.security_groups
        db_mysql = rds.DatabaseInstance(self, "MySQL_DB",
                                             engine=rds.DatabaseInstanceEngine.MYSQL,
                                             engine_version="5.7.22",
                                             instance_class=ec2.InstanceType.of(
                                                 ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.SMALL),
                                             master_username="admin",
                                             vpc=vpc,
                                             multi_az=True,
                                             allocated_storage=100,
                                             storage_type=rds.StorageType.GP2,
                                             cloudwatch_logs_exports=["audit", "error", "general", "slowquery"],
                                             deletion_protection=False,
                                             delete_automated_backups=False,
                                             backup_retention=core.Duration.days(7),
                                             removal_policy=core.RemovalPolicy.DESTROY,
                                             parameter_group=rds.ParameterGroup.from_parameter_group_name(
                                                 self, "para-group-mysql",
                                                 parameter_group_name="default.mysql5.7"
                                             )
                                             )
        for asg_sg in asg_security_groups:
            db_mysql.connections.allow_default_port_from(asg_sg, "EC2 Autoscaling Group access MySQL")   