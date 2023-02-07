""" 
Make sure you run these commands to setup your environment
pip install aws_cdk.aws_iam
pip install aws_cdk.aws_elasticache
pip install redis

Exercise for lab user: add Redis client code to put a key/value pair to the
Redis cluster and then do a get to retrieve your value by passing the key to your get 
api call. Then add an RDS or DynamoDB database and connect your Redis cluster to your data store.
"""
from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_elasticache as elasti
)

from aws_cdk.aws_iam import (
    Role,
    ServicePrincipal,
    ManagedPolicy,
    PolicyStatement
)


class HiAvailCdkStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, *, stack_tag="default", **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # create VPC w/ public, private, and isolated subnets in 2 AZs
        #     this also creates NAT Gateways in our public subnets
        vpc = ec2.Vpc(
            self, stack_tag,
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

        # Iterate the isolated subnets
        selection = vpc.select_subnets(
            subnet_type=ec2.SubnetType.ISOLATED
        )

        # Create our subnet group for our Redis cluster
        redis_subnet_group = elasti.CfnSubnetGroup(self, 'redis-subnet-group',
            description='The redis subnet group id',
            subnet_ids=selection.subnet_ids,
            cache_subnet_group_name='redis-subnet-group'
        )

        # Create our security group for our Redis cluster
        redis_security_group = ec2.SecurityGroup(self, 'redis-security-group', vpc=vpc,
        description="allow access to cluster", allow_all_outbound=True)

        # Create our Redis cluster
        redis = elasti.CfnCacheCluster(self, "redis-cluster", 
                cache_node_type='cache.t2.micro',
                engine='redis',
                engine_version='5.0.6',
                num_cache_nodes=1,
                port=6379,
                cache_subnet_group_name=redis_subnet_group.cache_subnet_group_name,
                vpc_security_group_ids=[redis_security_group.security_group_id]
                )
        redis.add_depends_on(redis_subnet_group)
        