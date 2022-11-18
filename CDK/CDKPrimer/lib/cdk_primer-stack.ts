import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ecs_patterns from 'aws-cdk-lib/aws-ecs-patterns';
// import * as sqs from 

export class CdkPrimerStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const vpc = new ec2.Vpc(this, "MyVpc", {maxAzs: 2});

    const cluster = new ecs.Cluster(this, "MyCluster", {vpc: vpc});

      new ecs_patterns.ApplicationLoadBalancedFargateService(this, "MyFargateService", {

          cluster: cluster,

          taskImageOptions: { image: ecs.ContainerImage.fromRegistry("amazon/amazon-ecs-sample") },

          publicLoadBalancer: true

  });
  }
}
