import boto3
import json
import argparse
import time

region_aws = 'us-east-1'

ec2 = boto3.resource('ec2', region_name=region_aws)
ec2_client = boto3.client('ec2', region_name=region_aws)
iam = boto3.client('iam', region_name=region_aws)
ssm = boto3.client('ssm', region_name=region_aws)

def create_ec2_ssm(vpc_id, subnet_id=None):

    # Create a role
    role_name = 'SSM-Role-EC2'
    policy_document = {
    "Version": "2012-10-17",
    "Statement": [
            {   
                "Effect": "Allow",
                "Principal": {
                "Service": "ec2.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }

    instance_profile_name = 'Profile-SSM-Role'
    
    if not role_name in [role['RoleName'] for role in iam.list_roles()['Roles']]:
        ssm_role = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(policy_document)
        )

        # Attach the policy to the role
        response = iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore'
        )

        # Create an instance profile
        instance_profile = iam.create_instance_profile(
            InstanceProfileName=instance_profile_name
        )
        # Add the role that you created to the instance profile:
        response = iam.add_role_to_instance_profile(
            InstanceProfileName=instance_profile_name,
            RoleName=role_name
        )

    # Select a vpc
    vpc = ec2.Vpc(vpc_id)

    # Select a subnet
    if not subnet_id:
        subnet = list(vpc.subnets.all())[0]

    role_name = 'Instance-SG-HTTPS'
    sg = [sg for sg in vpc.security_groups.all() if sg.group_name == role_name]

    # Create security group enable HHTPS:
    if not sg:
        security_group_https = vpc.create_security_group(
            GroupName=role_name,
            Description='Allow HTTPS access',
            VpcId=vpc.id,
        )

        response = ec2_client.authorize_security_group_ingress(
            GroupId=security_group_https.id,
            IpPermissions=[
                {'FromPort': 443,
                    'IpProtocol': 'tcp',
                    'IpRanges': [
                        {
                            'CidrIp': vpc.cidr_block,
                            'Description': 'Allow HTTPS access'
                        }
                    ],
                    'ToPort': 443
                }
            ]
        )
    else:
        security_group_https = sg[0]

    # Search for the latest Amazon Linux 2 AMI
    ssm_response = ssm.get_parameter(
        Name='/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2'
    )

    # Create a key pair
    key_name = 'KeyPair-Instance-SSM'
    key_pair_created = False

    if key_name not in [key_pair.key_name for key_pair in ec2.key_pairs.all()]:
        key_pair = ec2.create_key_pair(KeyName=key_name)
        key_pair_file = open(key_name + '.pem', 'w')
        key_pair_file.write(key_pair.key_material)
        key_pair_file.close()
        key_pair_created = True
    
    print("Creating EC2 instance with SSM agent...\n")
    instances = ec2.create_instances(
        ImageId=ssm_response['Parameter']['Value'],
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        KeyName=key_name,
        SubnetId=subnet.id,
        IamInstanceProfile={
            'Name': instance_profile_name
        },
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'Cookbook-SSM-Instance'
                    },
                ]
            },
        ]
    )

    # Wait for the instance to enter the running state
    print("Waiting for the instance to enter the running state...")
    instances[0].wait_until_running()
    print("Instance is running...\n")

    # Enable Dns in VPC
    vpc.modify_attribute(EnableDnsSupport={'Value': True})
    vpc.modify_attribute(EnableDnsHostnames={'Value': True})
    
    # List of endpoints filter by VPC
    list_endpoints = []
    ssmpr = f"com.amazonaws.{region_aws}.ssm"
    ec2msg = f"com.amazonaws.{region_aws}.ec2messages"
    ssmmsg = f"com.amazonaws.{region_aws}.ssmmessages"

    for endpoint in ec2_client.describe_vpc_endpoints()['VpcEndpoints']:
        if endpoint['VpcId'] == vpc.id:
            list_endpoints.append(endpoint['ServiceName'])
    
    # Creates a VPC endpoint for SSM:
    if not ssmpr in list_endpoints:        
        vpc_endpoint_ssm = ec2_client.create_vpc_endpoint(
            VpcId=vpc.id,
            ServiceName='com.amazonaws.' + region_aws + '.ssm',
            VpcEndpointType='Interface',
            SubnetIds=[subnet.id],
            PrivateDnsEnabled=True,
            SecurityGroupIds=[security_group_https.id]
        )
    
    if not ec2msg in list_endpoints:
        # Creates a VPC endpoint for EC2 messages:
        vpc_endpoint_ec2msg = ec2_client.create_vpc_endpoint(
            VpcId=vpc.id,
            ServiceName='com.amazonaws.' + region_aws + '.ec2messages',
            VpcEndpointType='Interface',
            SubnetIds=[subnet.id],
            PrivateDnsEnabled=True,
            SecurityGroupIds=[security_group_https.id]
        )
    
    if not ssmmsg in list_endpoints:
        # Creates a VPC endpoint for SSMMessages:
        vpc_endpoint_ssm = ec2_client.create_vpc_endpoint(
            VpcId=vpc.id,
            ServiceName='com.amazonaws.' + region_aws + '.ssmmessages',
            VpcEndpointType='Interface',
            SubnetIds=[subnet.id],
            PrivateDnsEnabled=True,
            SecurityGroupIds=[security_group_https.id]
        )
        # Wait for the VPC endpoints to be available:
        while vpc_endpoint_status(vpc_endpoint_ssm['VpcEndpoint']['VpcEndpointId']) != 'available':
            print('Waiting for VPC endpoints to be available...')
            time.sleep(30)
        print('VPC endpoints are available')


    wait_instance_ssm = len(ssm.describe_instance_information()['InstanceInformationList'])

    while wait_instance_ssm == 0:
        print('Waiting for EC2-SSM connection to be available...')
        time.sleep(10)
        print('Press Ctrl-C to stop waiting')
        wait_instance_ssm = len(ssm.describe_instance_information()['InstanceInformationList'])

    instance_id = ssm.describe_instance_information()['InstanceInformationList'][0]['InstanceId']
    print("\nIn the terminal execute the following command to connect to the instance:")
    print("   aws ssm start-session --target " + instance_id)
    print("\n\n")

    if key_pair_created:
        print("\nKey pair already created: " + key_name + ".pem")


def vpc_endpoint_status(vpc_endpoint_id):
    vpc_endpoint = ec2_client.describe_vpc_endpoints(
        VpcEndpointIds=[vpc_endpoint_id]
    )
    return vpc_endpoint['VpcEndpoints'][0]['State']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create an EC2 instance with SSM role')
    parser.add_argument('--vpc-id', required=True, help='VPC ID')
    parser.add_argument('--subnet-id', help='Subnet ID')

    args = parser.parse_args()
    create_ec2_ssm(args.vpc_id, args.subnet_id)
