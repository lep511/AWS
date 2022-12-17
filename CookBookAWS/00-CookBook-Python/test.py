### Habilitación de las conexiones Cross-VPC transitivas mediante gateway de tránsito

#### Problema
Necesita implementar el enrutamiento transitivo a través de todas sus VPCs y compartir la salida de Internet desde una VPC de servicios compartidos a sus otras VPCs para reducir el número de gateways NAT que tiene que implementar. 

#### Solución
Implemente una gateway de tránsito de AWS (TGW) y configure los anexos de la VPC de la gateway de tránsito para todas sus VPC. Actualice sus tablas de rutas de VPC de cada VPC para enviar todo el tráfico no local a la gateway de tránsito y habilite el uso compartido de la gateway de NAT en su VPC de servicios compartidos para todas sus VPCs de radio.
<br>
<br>
<img src="https://learning.oreilly.com/api/v2/epubs/urn:orm:book:9781492092599/files/assets/awsc_0214.png" width="600">
**NOTA:** La cuota inicial por defecto de VPCs por Región por cuenta es de cinco. Esta solución desplegará tres VPCs. Si ya tiene más de dos VPC, puede decidir entre cuatro opciones: desplegar en una Región diferente, eliminar cualquier VPC existente que ya no sea necesaria, utilizar una cuenta de prueba o solicitar un aumento de cuota.
import boto3
import json
import time

region_aws = 'us-east-1'

ec2 = boto3.resource('ec2', region_name=region_aws)
ec2_client = boto3.client('ec2', region_name=region_aws)
# create 3 VPC
vpc1 = ec2.create_vpc(CidrBlock='10.10.0.0/16')
vpc1.create_tags(Tags=[{"Key": "Name", "Value": "AWSCookBookVPC-1"}])
vpc2 = ec2.create_vpc(CidrBlock='10.11.0.0/16')
vpc2.create_tags(Tags=[{"Key": "Name", "Value": "AWSCookBookVPC-2"}])
vpc3 = ec2.create_vpc(CidrBlock='10.12.0.0/16')
vpc3.create_tags(Tags=[{"Key": "Name", "Value": "AWSCookBookVPC-3"}])
vpc3.wait_until_available()
# Crear 4 subredes para VPC1
vpc1_subnet_private1 = ec2.create_subnet(
    CidrBlock='10.10.0.0/24', 
    VpcId=vpc1.id,
    AvailabilityZone='us-east-1a'
)
vpc1_subnet_private2 = ec2.create_subnet(
    CidrBlock='10.10.1.0/24',
    VpcId=vpc1.id,
    AvailabilityZone='us-east-1b'
)
vpc1_subnet_private_att_1 = ec2.create_subnet(
    CidrBlock='10.10.2.0/24', 
    VpcId=vpc1.id,
    AvailabilityZone='us-east-1a'
)
vpc1_subnet_private_att_2 = ec2.create_subnet(
    CidrBlock='10.10.3.0/24',
    VpcId=vpc1.id,
    AvailabilityZone='us-east-1b'
)
# Create tags
vpc1_subnet_private1.create_tags(Tags=[{"Key": "Name", "Value": "AWSCookBookVPC-1-Private-1"}])
vpc1_subnet_private2.create_tags(Tags=[{"Key": "Name", "Value": "AWSCookBookVPC-1-Private-2"}])
vpc1_subnet_private_att_1.create_tags(Tags=[{"Key": "Name", "Value": "AWSCookBookVPC-1-Private-Attach-1"}])
vpc1_subnet_private_att_2.create_tags(Tags=[{"Key": "Name", "Value": "AWSCookBookVPC-1-Private-Attach-2"}])
# Cree 6 subredes para VPC2:
vpc2_subnet_public1 = ec2.create_subnet(
    CidrBlock='10.11.0.0/24', 
    VpcId=vpc2.id,
    AvailabilityZone='us-east-1a'
)
vpc2_subnet_public2 = ec2.create_subnet(
    CidrBlock='10.11.1.0/24',
    VpcId=vpc2.id,
    AvailabilityZone='us-east-1b'
)
vpc2_subnet_private1 = ec2.create_subnet(
    CidrBlock='10.11.2.0/24', 
    VpcId=vpc2.id,
    AvailabilityZone='us-east-1a'
)
vpc2_subnet_private2 = ec2.create_subnet(
    CidrBlock='10.11.3.0/24',
    VpcId=vpc2.id,
    AvailabilityZone='us-east-1b'
)
vpc2_subnet_private_att_1 = ec2.create_subnet(
    CidrBlock='10.11.4.0/24',
    VpcId=vpc2.id,
    AvailabilityZone='us-east-1a'
)
vpc2_subnet_private_att_2 = ec2.create_subnet(
    CidrBlock='10.11.5.0/24',
    VpcId=vpc2.id,
    AvailabilityZone='us-east-1b'
)
# Create tags
vpc2_subnet_public1.create_tags(Tags=[{"Key": "Name", "Value": "AWSCookBookVPC-2-Public-1"}])
vpc2_subnet_public2.create_tags(Tags=[{"Key": "Name", "Value": "AWSCookBookVPC-2-Public-2"}])
vpc2_subnet_private1.create_tags(Tags=[{"Key": "Name", "Value": "AWSCookBookVPC-2-Private-1"}])
vpc2_subnet_private2.create_tags(Tags=[{"Key": "Name", "Value": "AWSCookBookVPC-2-Private-2"}])
vpc2_subnet_private_att_1.create_tags(Tags=[{"Key": "Name", "Value": "AWSCookBookVPC-2-Private-Attach-1"}])
vpc2_subnet_private_att_2.create_tags(Tags=[{"Key": "Name", "Value": "AWSCookBookVPC-2-Private-Attach-2"}])
# Cree 4 subredes para VPC3:
vpc3_subnet_private1 = ec2.create_subnet(
    CidrBlock='10.12.0.0/24', 
    VpcId=vpc3.id,
    AvailabilityZone='us-east-1a'
)
vpc3_subnet_private2 = ec2.create_subnet(
    CidrBlock='10.12.1.0/24',
    VpcId=vpc3.id,
    AvailabilityZone='us-east-1b'
)
vpc3_subnet_private_att_1 = ec2.create_subnet(
    CidrBlock='10.12.2.0/24', 
    VpcId=vpc3.id,
    AvailabilityZone='us-east-1a'
)
vpc3_subnet_private_att_2 = ec2.create_subnet(
    CidrBlock='10.12.3.0/24',
    VpcId=vpc3.id,
    AvailabilityZone='us-east-1b'
)
# Create tags
vpc3_subnet_private1.create_tags(Tags=[{"Key": "Name", "Value": "AWSCookBookVPC-3-Private-1"}])
vpc3_subnet_private2.create_tags(Tags=[{"Key": "Name", "Value": "AWSCookBookVPC-3-Private-2"}])
vpc3_subnet_private_att_1.create_tags(Tags=[{"Key": "Name", "Value": "AWSCookBookVPC-3-Private-Attach-1"}])
vpc3_subnet_private_att_2.create_tags(Tags=[{"Key": "Name", "Value": "AWSCookBookVPC-3-Private-Attach-2"}])

# Crear routables para VPC1
vpc1_route_table_private_1 = ec2.create_route_table(VpcId=vpc1.id)
vpc1_route_table_private_1.create_tags(Tags=[{"Key": "Name", "Value": "AWSCookBookVPC-1-Private-Route-Table-a"}])
vpc1_route_table_private_2 = ec2.create_route_table(VpcId=vpc1.id)
vpc1_route_table_private_2.create_tags(Tags=[{"Key": "Name", "Value": "AWSCookBookVPC-1-Private-Route-Table-b"}])


# Crear routables para VPC2
vpc2_route_table_public = ec2.create_route_table(VpcId=vpc2.id)
vpc2_route_table_public.create_tags(Tags=[{"Key": "Name", "Value": "AWSCookBookVPC-Public-Route-Table"}])
vpc2_route_table_private_1 = ec2.create_route_table(VpcId=vpc2.id)
vpc2_route_table_private_1.create_tags(Tags=[{"Key": "Name", "Value": "AWSCookBookVPC-2-Private-Route-Table-a"}])
vpc2_route_table_private_2 = ec2.create_route_table(VpcId=vpc2.id)
vpc2_route_table_private_2.create_tags(Tags=[{"Key": "Name", "Value": "AWSCookBookVPC-2-Private-Route-Table-b"}])

# Crear routables para VPC3
vpc3_route_table_private_1 = ec2.create_route_table(VpcId=vpc3.id)
vpc3_route_table_private_1.create_tags(Tags=[{"Key": "Name", "Value": "AWSCookBookVPC-3-Private-Route-Table-a"}])
vpc3_route_table_private_2 = ec2.create_route_table(VpcId=vpc3.id)
vpc3_route_table_private_2.create_tags(Tags=[{"Key": "Name", "Value": "AWSCookBookVPC-3-Private-Route-Table-b"}])

# Asoociar la tabla de rutas a la subred privada de VPC1
vpc1_route_table_private_1.associate_with_subnet(SubnetId=vpc1_subnet_private1.id)
vpc1_route_table_private_2.associate_with_subnet(SubnetId=vpc1_subnet_private2.id)


# Asoociar la tabla de rutas a la subred privada de VPC2
vpc2_route_table_private_1.associate_with_subnet(SubnetId=vpc2_subnet_private1.id)
vpc2_route_table_private_2.associate_with_subnet(SubnetId=vpc2_subnet_private2.id)


# Asoociar la tabla de rutas a la subred privada de VPC3
vpc3_route_table_private_1.associate_with_subnet(SubnetId=vpc3_subnet_private1.id)
vpc3_route_table_private_2.associate_with_subnet(SubnetId=vpc3_subnet_private2.id)


# Asoociar la tabla de rutas a la subred publica de VPC2
vpc2_route_table_public.associate_with_subnet(SubnetId=vpc2_subnet_public1.id)
vpc2_route_table_public.associate_with_subnet(SubnetId=vpc2_subnet_public2.id)
# Create 2 elastic IP
eip1 = ec2_client.allocate_address(Domain='vpc')
eip2 = ec2_client.allocate_address(Domain='vpc')
# Create 2 NAT Gateways
nat1 = ec2_client.create_nat_gateway(
    AllocationId=eip1['AllocationId'],
    SubnetId=vpc2_subnet_public1.id
)
nat2 = ec2_client.create_nat_gateway(
    AllocationId=eip2['AllocationId'],
    SubnetId=vpc2_subnet_public2.id
)
# create 1 internet gateways
igw = ec2.create_internet_gateway()
igw.create_tags(Tags=[{"Key": "Name", "Value": "AWSCookBookIGW"}])
# attach internet gateway to VPC N° 2
vpc2.attach_internet_gateway(InternetGatewayId=igw.id)
#### Crear un gateway de tránsito
tgw = ec2_client.create_transit_gateway(
    Description='AWSCookBookTGW',
    Options={
        'AmazonSideAsn': 65010,
        'AutoAcceptSharedAttachments': 'enable',
        'DefaultRouteTableAssociation': 'enable',
        'DefaultRouteTablePropagation': 'enable',
        'DnsSupport': 'enable',
        'VpnEcmpSupport': 'enable'
    }
)
# Tag the transit gateway
response = ec2_client.create_tags(
    Resources=[tgw['TransitGateway']['TransitGatewayId']],
    Tags=[{'Key': 'Name', 'Value': 'AWSCookBookTGW'}]
)
Espere hasta que el estado del gateway de tránsito esté disponible. Esto puede tardar varios minutos:
state = "pending"
print(tgw_state['TransitGateways'][0]['State'] + "...")
while state == "pending":
    # Describe the transit gateway
    tgw_state = ec2_client.describe_transit_gateways(
        TransitGatewayIds=[
            tgw['TransitGateway']['TransitGatewayId'],
        ]
    )
    state = tgw_state['TransitGateways'][0]['State']
print(tgw_state['TransitGateways'][0]['State'])
# Create a transit gateway attachment for VPC1:
tgw_attachment_vpc1 = ec2_client.create_transit_gateway_vpc_attachment(
    TransitGatewayId=tgw['TransitGateway']['TransitGatewayId'],
    VpcId=vpc1.id,
    SubnetIds=[
        vpc1_subnet_private_att_1.id,
        vpc1_subnet_private_att_2.id,
    ],
)
# Create a transit gateway attachment for VPC2:
tgw_attachment_vpc2 = ec2_client.create_transit_gateway_vpc_attachment(
    TransitGatewayId=tgw['TransitGateway']['TransitGatewayId'],
    VpcId=vpc2.id,
    SubnetIds=[
        vpc2_subnet_private_att_1.id,
        vpc2_subnet_private_att_2.id,
    ],
)
# Create a transit gateway attachment for VPC3:
tgw_attachment_vpc3 = ec2_client.create_transit_gateway_vpc_attachment(
    TransitGatewayId=tgw['TransitGateway']['TransitGatewayId'],
    VpcId=vpc3.id,
    SubnetIds=[
        vpc3_subnet_private_att_1.id,
        vpc3_subnet_private_att_2.id,
    ],
)
# Create Tags for the transit gateway attachments
response = ec2_client.create_tags(
    Resources=[
        tgw_attachment_vpc1['TransitGatewayVpcAttachment']['TransitGatewayAttachmentId']
    ],
    Tags=[
        {'Key': 'Name', 'Value': 'AWSCookBookTGW-Attachment-VPC1'}
    ]
)

response = ec2_client.create_tags(
    Resources=[
        tgw_attachment_vpc2['TransitGatewayVpcAttachment']['TransitGatewayAttachmentId']
    ],
    Tags=[
        {'Key': 'Name', 'Value': 'AWSCookBookTGW-Attachment-VPC2'}
    ]
)

response = ec2_client.create_tags(
    Resources=[
        tgw_attachment_vpc3['TransitGatewayVpcAttachment']['TransitGatewayAttachmentId']
    ],
    Tags=[
        {'Key': 'Name', 'Value': 'AWSCookBookTGW-Attachment-VPC3'}
    ]
)

# Añade rutas para todas las subredes privadas en las VPCs 1 y 3 para apuntar al TGW para destinos de 0.0.0.0/0. 
# Esto permite la salida consolidada de Internet a través de la puerta de enlace 
# NAT en la VPC2 y el enrutamiento transitivo a otras VPCs:

vpc1_route_table_private_1.create_route(
    DestinationCidrBlock='0.0.0.0/0',
    TransitGatewayId=tgw['TransitGateway']['TransitGatewayId']
)
vpc1_route_table_private_2.create_route(
    DestinationCidrBlock='0.0.0.0/0',
    TransitGatewayId=tgw['TransitGateway']['TransitGatewayId']
)
vpc3_route_table_private_1.create_route(
    DestinationCidrBlock='0.0.0.0/0',
    TransitGatewayId=tgw['TransitGateway']['TransitGatewayId']
)
vpc3_route_table_private_2.create_route(
    DestinationCidrBlock='0.0.0.0/0',
    TransitGatewayId=tgw['TransitGateway']['TransitGatewayId']
)
# Ahora añade una ruta a tu superred 10.10.0.0/24 en las tablas de rutas asociadas a las subredes privadas de la VPC2, 
# apuntando su destino a la gateway de tránsito. Esto es más específico que el destino 0.0.0.0/0 que ya está presente y, 
# por lo tanto, tiene mayor prioridad en las decisiones de enrutamiento. Esto dirige el tráfico 
# con destino a las VPC 1, 2 y 3 al TGW:

vpc2_route_table_private_1.create_route(
    DestinationCidrBlock='10.10.0.0/24',
    TransitGatewayId=tgw['TransitGateway']['TransitGatewayId']
)
vpc2_route_table_private_2.create_route(
    DestinationCidrBlock='10.10.0.0/24',
    TransitGatewayId=tgw['TransitGateway']['TransitGatewayId']
)

# Consulta las gateways NAT en uso; las necesitaremos para añadir rutas a ellas para el tráfico de Internet:
nat1_id = nat1['NatGateway']['NatGatewayId']
nat2_id = nat2['NatGateway']['NatGatewayId']

# Add a route for the attachment subnet in VPC2 to direct internet traffic to the NAT gateway:
vpc2_route_table_private_1.create_route(
    DestinationCidrBlock='0.0.0.0/0',
    NatGatewayId=nat1_id
)
vpc2_route_table_private_2.create_route(
    DestinationCidrBlock='0.0.0.0/0',
    NatGatewayId=nat1_id
)

# Add a static route to the route tables associated with the public subnet in VPC2. This enables communication back to the TGW to allow sharing the NAT gateway with all attached VPCs:
vpc2_route_table_public.create_route(
    DestinationCidrBlock='10.10.0.0/24',
    TransitGatewayId=tgw['TransitGateway']['TransitGatewayId']
)

# Add a static route for the private subnets in VPC2 to allow communication back to the TGW attachments from VPC2 private subnets:
vpc2_route_table_private_1.create_route(
    DestinationCidrBlock='10.10.0.0/24',
    TransitGatewayId=tgw['TransitGateway']['TransitGatewayId']
)
vpc2_route_table_private_2.create_route(
    DestinationCidrBlock='10.10.0.0/24',
    TransitGatewayId=tgw['TransitGateway']['TransitGatewayId']
)

# Get the transit route table ID:
tgw_route_table_id = tgw['TransitGateway']['Associations'][0]['TransitGatewayRouteTableId']

# Add a static route in the transit gateway route table for VPC2 (with the NAT gateways) to send all internet traffic over this path:
response = ec2_client.create_transit_gateway_route(
    TransitGatewayRouteTableId=tgw_route_table_id,
    DestinationCidrBlock='0.0.0.0/0',
    TransitGatewayAttachmentId=tgw_attachment_vpc2['TransitGatewayVpcAttachment']['TransitGatewayAttachmentId']
)

