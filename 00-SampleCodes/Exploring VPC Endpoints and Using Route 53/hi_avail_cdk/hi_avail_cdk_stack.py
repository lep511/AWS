""" 
Make sure you install all of the aws packages listed in the import statement 
by running pip install commands following this pattern:
pip install aws_cdk.aws_<service name> 
where <service name> is the name of each package, such as ec2
"""

from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_route53 as route53,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    aws_route53_targets as targets,
    aws_elasticloadbalancingv2 as elbv2,
    core,
)


class HiAvailCdkStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, *, stack_tag="default", **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Route 53 example
        website_bucket = s3.Bucket(self, "BucketWebsite",
            bucket_name="www.portfoliovbl.com",
            website_index_document="index.html",
            public_read_access=True
        )

        s3deploy.BucketDeployment(self, "DeployWebsite",
            sources=[s3deploy.Source.asset("./user_data/portfolio.zip")],
            destination_bucket=website_bucket,
            # destination_key_prefix="web/static"
        )
        
        my_zone = route53.PublicHostedZone(self, "HostedZone",
            zone_name="portfoliovbl.com"
        )

        route53.ARecord(self, "AlaisRecord",
            zone=my_zone,
            record_name="www",
            target=route53.RecordTarget.from_alias(targets.BucketWebsiteTarget(website_bucket))
        )

        # VPC Endpoints example
        # Add gateway endpoints when creating the VPC
        vpc = ec2.Vpc(self, "MyVpcWithEndpoints",
            gateway_endpoints={
                "S3": ec2.GatewayVpcEndpointOptions(
                    service=ec2.GatewayVpcEndpointAwsService.S3
                )
            }
        )

        # Gateway endpoints can also be added on the VPC
        dynamo_db_endpoint = vpc.add_gateway_endpoint("DynamoDbEndpoint",
            service=ec2.GatewayVpcEndpointAwsService.DYNAMODB
        )

        # This allows for customization of the endpoint policy
        dynamo_db_endpoint.add_to_policy(
            iam.PolicyStatement(# Restricted to listing and describing tables
                principals=[iam.AnyPrincipal()],
                actions=["dynamodb:DescribeTable", "dynamodb:ListTables"],
                resources=["*"]))

        # Can also add an interface endpoint
        vpc.add_interface_endpoint("EcrDockerEndpoint", 
            service=ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER
        )

        # Example of providing a service to consumers over a network load balancer(s), such as our SaaS example
        network_load_balancer_SaaS = elbv2.NetworkLoadBalancer(self, "LB_SaaS",
            vpc=vpc,
            internet_facing=True
        )

        ec2.VpcEndpointService(self, "EndpointService",
            vpc_endpoint_service_load_balancers=[network_load_balancer_SaaS],
            acceptance_required=True,
            whitelisted_principals=[iam.ArnPrincipal("arn:aws:iam::123456789012:root")]
        )
