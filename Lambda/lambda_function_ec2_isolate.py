"""
This lambda function isolates the instance 
for further forensic analysis.
"""
import os, json
import boto3
import logging

# It is a good practice to use proper logging.
# Here we are using the logging module of python.
# https://docs.python.org/3/library/logging.html

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ec2_client = boto3.client('ec2')
ec2_resource = boto3.resource('ec2')
instance_list = []

def lambda_handler(event, context):
    print(json.dumps(event))
    
    # Find the instance ID from MetricName defined 
    # in the Cloudwatch Alarm configuration. MetricName should be set to the instance-id.
    
    message = json.loads(event['Records'][0]["Sns"].get('Message'))
    instance_id = message['Trigger'].get('MetricName')
    logger.info(instance_id)
    
    # Get the VPC of the instance
    vpcId = get_instace_vpc_id(instance_id)
    
    # Call the get_instance function to generate list of all the available instances.
    get_instances()
    
    # If the instance is in the list, remove role 
    # and attach the Isolated_SG
    if instance_id in instance_list:
        try:
            remove_role(instance_id)
        except Exception as e:
            print(e)
    
        # Attach the isolated Security group
        try:
            sg_response = ec2_client.describe_security_groups(
            Filters=[
                    {
                        'Name': 'group-name',
                        'Values': [
                            'Isolated_SG',
                        ]
                    },
                ]
                )
            logger.info(sg_response)    
            if sg_response.get('SecurityGroups'):
                security_group_id = sg_response.get('SecurityGroups')[0].get("GroupId")
                logger(security_group_id)
                attach_isolated_sg(instance_id, security_group_id)
            else:
                security_group_id = create_sg(vpcId)
                attach_isolated_sg(instance_id, security_group_id)
        except Exception as e:
            print(e)
    

def get_instances():
    """
    This function gets the list of all the EC2 instances in the region.
    """
    get_instances = ec2_client.describe_instances()
    instances = get_instances['Reservations'][0].get('Instances')
    print(instances)
    for instance in instances:
        print(instance['InstanceId'])
        # print(instance['VpcId'])
        instance_id = instance['InstanceId']
        instance_list.append(instance_id)
    print(f"instance-List:{instance_list}")
    
def remove_role(instance_id):
    """
    This function removed the instance proflie attached to the instance.
    """
    describe_instance_profile_association_response = ec2_client.describe_iam_instance_profile_associations(
        Filters=[
                {
                    'Name': 'instance-id',
                    'Values': [
                        instance_id,
                    ]
                },
            ]
        )
    print(describe_instance_profile_association_response)
    association_id = describe_instance_profile_association_response['IamInstanceProfileAssociations'][0].get('AssociationId')
    
    print(association_id)
    response = ec2_client.disassociate_iam_instance_profile(
            AssociationId=association_id
            )
    
    logger.info(response)
    
    
def get_instace_vpc_id(instanceId):
    """
    This function gets the VPC Id of the instance.
    """
    instanceReservations = ec2_client.describe_instances(InstanceIds=[instanceId])['Reservations']
    for instanceReservation in instanceReservations:
        instancesDescription = instanceReservation['Instances']
        for instance in instancesDescription:
            return instance['VpcId']
            
def create_sg(vpcId):
    """
    This function creates the isolated security group with no egress access.
    """
    security_group_id = ec2_resource.create_security_group(GroupName="Isolated_SG", 
                                                     Description="Isolated SG for forensic analysis", 
                                                     VpcId=vpcId)
    security_group_id.revoke_egress(IpPermissions= [{'IpProtocol': '-1','IpRanges': [{'CidrIp': '0.0.0.0/0'}],'Ipv6Ranges': [],'PrefixListIds': [],'UserIdGroupPairs': []}])
    return security_group_id

def attach_isolated_sg(instance_id, security_group_id):
    """
    This function attach the isolated security group to the instance.
    """

    logger.info("Inside attach_sg")
    logger.info(security_group_id.id)
    
    
    response = ec2_client.modify_instance_attribute(
        Groups=[security_group_id.id],
        InstanceId=instance_id)
