#!/usr/bin/env python3

from aws_cdk import core

from hi_avail_cdk.hi_avail_cdk_stack import HiAvailCdkStack
from hi_avail_cdk.hi_avail_eks_cdk_stack import HiAvailEksCdkStack

app = core.App()
HiAvailCdkStack(app, "hi-avail-cdk-east", env=core.Environment(region="us-east-1"), stack_tag="UsEastStack")
HiAvailEksCdkStack(app, "hi-avail-eks-cdk-east", env=core.Environment(region="us-east-1"), stack_tag="UsEastStack")

app.synth()
