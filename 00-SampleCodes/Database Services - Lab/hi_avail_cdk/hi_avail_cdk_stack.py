""" 
Make sure you run these commands to setup your environment
pip install paho-mqtt 
pip install requests
pip install appsync-client
pip install aws_cdk.aws_appsync
pip install aws_cdk.aws_iam
pip install aws_cdk.aws_dynamodb

Exercise for lab user: use the 'products' set of queries and load data
into the products table using the suplied GraphQL api. Then aggregate the data
from the Items and Products table in additional resolver code
"""
from aws_cdk import core
from aws_cdk.aws_appsync import (
    CfnGraphQLSchema,
    CfnGraphQLApi,
    CfnApiKey,
    CfnDataSource,
    CfnResolver
)
from aws_cdk.aws_dynamodb import (
    Table,
    Attribute,
    AttributeType,
    StreamViewType,
    BillingMode
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

        # Define our table names
        first_table = 'items2'
        second_table = 'products'

        # Define our APIs
        items_graphql_api = CfnGraphQLApi(
            self, 'Items2Api',
            name='items2-api',
            authentication_type='API_KEY'
        )

        products_graphql_api = CfnGraphQLApi(
            self, 'ProductsApi',
            name='products-api',
            authentication_type='API_KEY'
        )

        CfnApiKey(
            self, 'Items2ApiKey',
            api_id=items_graphql_api.attr_api_id
        )

        CfnApiKey(
            self, 'ProductsApiKey',
            api_id=products_graphql_api.attr_api_id
        )

        # Define our API schemas
        api_schema = CfnGraphQLSchema(
            self, 'Items2Schema',
            api_id=items_graphql_api.attr_api_id,
            definition=f"""\
                type {first_table} {{
                    {first_table}Id: ID!
                    name: String
                }}
                type Paginated{first_table} {{
                    items: [{first_table}!]!
                    nextToken: String
                }}
                type Query {{
                    all(limit: Int, nextToken: String): Paginated{first_table}!
                    getOne({first_table}Id: ID!): {first_table}
                }}
                type Mutation {{
                    save(name: String!): {first_table}
                    delete({first_table}Id: ID!): {first_table}
                }}
                type Schema {{
                    query: Query
                    mutation: Mutation
                }}"""
        )

        products_api_schema = CfnGraphQLSchema(
            self, 'ProductsSchema',
            api_id=products_graphql_api.attr_api_id,
            definition=f"""\
                type {second_table} {{
                    {second_table}Id: ID!
                    name: String
                }}
                type Paginated{second_table} {{
                    items: [{second_table}!]!
                    nextToken: String
                }}
                type Query {{
                    all(limit: Int, nextToken: String): Paginated{second_table}!
                    getOne({second_table}Id: ID!): {second_table}
                }}
                type Mutation {{
                    save(name: String!): {second_table}
                    delete({second_table}Id: ID!): {second_table}
                }}
                type Schema {{
                    query: Query
                    mutation: Mutation
                }}"""
        )

        items_table = Table(
            self, 'Items2Table',
            table_name=first_table,
            partition_key=Attribute(
                name=f'{first_table}Id',
                type=AttributeType.STRING
            ),
            billing_mode=BillingMode.PAY_PER_REQUEST,
            stream=StreamViewType.NEW_IMAGE,

            removal_policy=core.RemovalPolicy.DESTROY # NOT recommended for production code
        )
        
        products_table = Table(
            self, 'ProductsTable',
            table_name=second_table,
            partition_key=Attribute(
                name=f'{second_table}Id',
                type=AttributeType.STRING
            ),
            billing_mode=BillingMode.PAY_PER_REQUEST,
            stream=StreamViewType.NEW_IMAGE,

            removal_policy=core.RemovalPolicy.DESTROY # NOT recommended for production code
        )

        items_table_role = Role(
            self, 'ItemsDynamoDBRole',
            assumed_by=ServicePrincipal('appsync.amazonaws.com')
        )

        role_id="mp" + stack_tag
        policy_name="AmazonDynamoDBFullAccess" + stack_tag

        items_table_role.add_managed_policy(ManagedPolicy(self, id=role_id, managed_policy_name=policy_name,
                                                  statements=[PolicyStatement(actions=['*'], resources=['*'])]))

        # Define our items data sources
        # Items data source
        data_source = CfnDataSource(
            self, 'Items2DataSource',
            api_id=items_graphql_api.attr_api_id,
            name='Items2DynamoDataSource',
            type='AMAZON_DYNAMODB',
            dynamo_db_config=CfnDataSource.DynamoDBConfigProperty(
                table_name=items_table.table_name,
                aws_region=self.region
            ),
            service_role_arn=items_table_role.role_arn
        )

        # Define our resolvers
        get_one_resolver = CfnResolver(
            self, 'GetOneQueryResolver',
            api_id=items_graphql_api.attr_api_id,
            type_name='Query',
            field_name='getOne',
            data_source_name=data_source.name,
            request_mapping_template=f"""\
            {{
                "version": "2017-02-28",
                "operation": "GetItem",
                "key": {{
                "{first_table}Id": $util.dynamodb.toDynamoDBJson($ctx.args.{first_table}Id)
                }}
            }}""",
            response_mapping_template="$util.toJson($ctx.result)"
        )

        get_one_resolver.add_depends_on(api_schema)

        get_all_resolver = CfnResolver(
            self, 'GetAllQueryResolver',
            api_id=items_graphql_api.attr_api_id,
            type_name='Query',
            field_name='all',
            data_source_name=data_source.name,
            request_mapping_template=f"""\
            {{
                "version": "2017-02-28",
                "operation": "Scan",
                "limit": $util.defaultIfNull($ctx.args.limit, 20),
                "nextToken": $util.toJson($util.defaultIfNullOrEmpty($ctx.args.nextToken, null))
            }}""",
            response_mapping_template="$util.toJson($ctx.result)"
        )

        get_all_resolver.add_depends_on(api_schema)

        save_resolver = CfnResolver(
            self, 'SaveMutationResolver',
            api_id=items_graphql_api.attr_api_id,
            type_name='Mutation',
            field_name='save',
            data_source_name=data_source.name,
            request_mapping_template=f"""\
            {{
                "version": "2017-02-28",
                "operation": "PutItem",
                "key": {{
                    "{first_table}Id": {{ "S": "$util.autoId()" }}
                }},
                "attributeValues": {{
                    "name": $util.dynamodb.toDynamoDBJson($ctx.args.name)
                }}
            }}""",
            response_mapping_template="$util.toJson($ctx.result)"
        )

        save_resolver.add_depends_on(api_schema)

        delete_resolver = CfnResolver(
            self, 'DeleteMutationResolver',
            api_id=items_graphql_api.attr_api_id,
            type_name='Mutation',
            field_name='delete',
            data_source_name=data_source.name,
            request_mapping_template=f"""\
            {{
                "version": "2017-02-28",
                "operation": "DeleteItem",
                "key": {{
                "{first_table}Id": $util.dynamodb.toDynamoDBJson($ctx.args.{first_table}Id)
                }}
            }}""",
            response_mapping_template="$util.toJson($ctx.result)"
        )

        delete_resolver.add_depends_on(api_schema)

        # Products data source
        # 
        products_data_source = CfnDataSource(
            self, 'ProductsDataSource',
            api_id=products_graphql_api.attr_api_id,
            name='ProductsDynamoDataSource',
            type='AMAZON_DYNAMODB',
            dynamo_db_config=CfnDataSource.DynamoDBConfigProperty(
                table_name=products_table.table_name,
                aws_region=self.region
            ),
            service_role_arn=items_table_role.role_arn
        )

        # Define our resolvers
        get_one_product_resolver = CfnResolver(
            self, 'GetOneProductQueryResolver',
            api_id=products_graphql_api.attr_api_id,
            type_name='Query',
            field_name='getOne',
            data_source_name=products_data_source.name,
            request_mapping_template=f"""\
            {{
                "version": "2017-02-28",
                "operation": "GetItem",
                "key": {{
                "{second_table}Id": $util.dynamodb.toDynamoDBJson($ctx.args.{second_table}Id)
                }}
            }}""",
            response_mapping_template="$util.toJson($ctx.result)"
        )

        get_one_product_resolver.add_depends_on(products_api_schema)

        get_all_products_resolver = CfnResolver(
            self, 'GetAllProductsQueryResolver',
            api_id=products_graphql_api.attr_api_id,
            type_name='Query',
            field_name='all',
            data_source_name=products_data_source.name,
            request_mapping_template=f"""\
            {{
                "version": "2017-02-28",
                "operation": "Scan",
                "limit": $util.defaultIfNull($ctx.args.limit, 20),
                "nextToken": $util.toJson($util.defaultIfNullOrEmpty($ctx.args.nextToken, null))
            }}""",
            response_mapping_template="$util.toJson($ctx.result)"
        )

        get_all_products_resolver.add_depends_on(products_api_schema)

        save_product_resolver = CfnResolver(
            self, 'SaveProductMutationResolver',
            api_id=products_graphql_api.attr_api_id,
            type_name='Mutation',
            field_name='save',
            data_source_name=products_data_source.name,
            request_mapping_template=f"""\
            {{
                "version": "2017-02-28",
                "operation": "PutItem",
                "key": {{
                    "{second_table}Id": {{ "S": "$util.autoId()" }}
                }},
                "attributeValues": {{
                    "name": $util.dynamodb.toDynamoDBJson($ctx.args.name)
                }}
            }}""",
            response_mapping_template="$util.toJson($ctx.result)"
        )

        save_product_resolver.add_depends_on(products_api_schema)

        delete_product_resolver = CfnResolver(
            self, 'DeleteProductMutationResolver',
            api_id=products_graphql_api.attr_api_id,
            type_name='Mutation',
            field_name='delete',
            data_source_name=products_data_source.name,
            request_mapping_template=f"""\
            {{
                "version": "2017-02-28",
                "operation": "DeleteItem",
                "key": {{
                "{second_table}Id": $util.dynamodb.toDynamoDBJson($ctx.args.{second_table}Id)
                }}
            }}""",
            response_mapping_template="$util.toJson($ctx.result)"
        )

        delete_product_resolver.add_depends_on(products_api_schema)