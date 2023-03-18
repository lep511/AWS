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
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_eks as eks,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_rds as rds,
    core,
)


class HiAvailEksCdkStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, *, stack_tag="default", **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # EKS exampple
        cluster = eks.FargateCluster(self, "MyCluster")

        app_label = {"app": "hello-vb-kubernetes"}

        deployment = {
            "api_version": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": "hello-vb-kubernetes"},
            "spec": {
                "replicas": 3,
                "selector": {"match_labels": app_label},
                "template": {
                    "metadata": {"labels": app_label},
                    "spec": {
                        "containers": [{
                            "name": "hello-vb-kubernetes",
                            "image": "paulbouwer/hello-kubernetes:1.5",
                            "ports": [{"container_port": 8080}]
                        }
                        ]
                    }
                }
            }
        }

        service = {
            "api_version": "v1",
            "kind": "Service",
            "metadata": {"name": "hello-vb-kubernetes"},
            "spec": {
                "type": "LoadBalancer",
                "ports": [{"port": 80, "target_port": 8080}],
                "selector": app_label
            }
        }

        # option2: use add_resource
        cluster.add_resource("hello-vb-kub", service, deployment)
        