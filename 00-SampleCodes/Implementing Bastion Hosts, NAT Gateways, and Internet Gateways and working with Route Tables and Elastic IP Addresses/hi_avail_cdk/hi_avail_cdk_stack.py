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

        # Configure the natGatewayProvider when defining a Vpc
        vpc = ec2.Vpc(self, "TheVPC",
            nat_gateways=3,
            # Define our VPC
            # 'cidr' configures the IP range and size of the entire VPC.
            # The IP space will be divided over the configured subnets.
            cidr="10.0.0.0/21",

            # 'maxAzs' configures the maximum number of availability zones to use
            max_azs=3,

            # 'subnetConfiguration' specifies the "subnet groups" to create.
            # Every subnet group will have a subnet for each AZ, so this
            # configuration will create 3 groups Ã— 3 AZs = 9 subnets.
            subnet_configuration=[ec2.SubnetConfiguration(
                # 'subnetType' controls Internet access, as described above.
                subnet_type=ec2.SubnetType.PUBLIC,

                # 'name' is used to name this particular subnet group. You will have to
                # use the name for subnet selection if you have more than one subnet
                # group of the same type.
                name="Pub",

                # 'cidrMask' specifies the IP addresses in the range of of individual
                # subnets in the group. Each of the subnets in this group will contain
                # 2^(32 address bits - 24 subnet bits) - 2 reserved addresses = 254
                # usable IP addresses.
                #
                # If 'cidrMask' is left out the available address space is evenly
                # divided across the remaining subnet groups.
                cidr_mask=24
            ), ec2.SubnetConfiguration(
                cidr_mask=24,
                name="App",
                subnet_type=ec2.SubnetType.PRIVATE
            ), ec2.SubnetConfiguration(
                cidr_mask=28,
                name="DB",
                subnet_type=ec2.SubnetType.ISOLATED,

                # 'reserved' can be used to reserve IP address space. No resources will
                # be created for this subnet, but the IP range will be kept available for
                # future creation of this subnet, or even for future subdivision.
                # reserved=True
            )
            ]
        )

        # To use the traditional Bastion host without SSM
        #host = ec2.BastionHostLinux(self, "BastionHost",
        #    vpc=vpc,
        #    subnet_selection=SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC)
        #)
        #host.allow_ssh_access_from(ec2.Peer.ipv4("1.2.3.4/32"))

        # Use Bastion host with SSM
        host = ec2.BastionHostLinux(self, "BastionHost", vpc=vpc)

        # Define the IAM role that will allow the EC2 instance to communicate with SSM
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
                                                desired_capacity=3,
                                                min_capacity=3,
                                                max_capacity=6,
                                                )

        asg.connections.allow_from(alb, ec2.Port.tcp(80), "ALB access port 80 of EC2 in Autoscaling Group")
        listener.add_targets("addTargetGroup",
                             port=80,
                             targets=[asg])

        # Scale to keep the CPU usage of your instances at around 50% utilization
        asg.scale_on_cpu_utilization("KeepSpareCPU",
                                     target_utilization_percent=50
                                     )