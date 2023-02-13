import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

# The Jobs parameters are received here
args = getResolvedOptions(sys.argv, ["JOB_NAME","es_user","es_pass","es_endpoint","input_bucket"])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)


# This section of the code create a DynamicFrame from 
# the the CSV files found in the input bucket.
# For more information on DynamicFrame see:
# https://docs.aws.amazon.com/glue/latest/dg/glue-etl-scala-apis-glue-dynamicframe-class.html 

TransactionsDF = glueContext.create_dynamic_frame.from_options(
    format_options={
        "quoteChar": '"',
        "withHeader": True,
        "separator": ",",
        "optimizePerformance": False,
    },
    connection_type="s3",
    compression="gzip", 
    format="csv",
    connection_options={
        "paths": [args['input_bucket']],
        "recurse": True,
    },
    transformation_ctx="TransactionsDF",
)

#  This sections creates the mappings for the transformation of the source DataFrame,
#  list of mapping tuples, each consisting of: (source column, source type, target column, target type)
#  with the mappings you can change the column name and its type from source to destination
#  To remove a unnecessary column that you don't want to index, remove one of the tuples (ex: line 53)

ApplyMapping  = ApplyMapping.apply(
    frame=TransactionsDF,
    mappings=[
        ("sequence_number", "long", "sequence_number", "long"),
        ("account_id", "long", "account_id", "long"),
        ("date", "string", "date", "string"),
        ("year", "long", "year", "long"),
        ("type", "string", "type", "string"),
        ("operation", "string", "operation", "string"),
        ("amount", "choice", "amount", "choice"),
        ("balance", "choice", "balance", "choice"),
        ("k_symbol", "string", "k_symbol", "string"),
    ],
    transformation_ctx="ApplyMapping",
)

DataFrame = ApplyMapping.toDF()

#  The following section write the records from the dataframe into the opensearch 
#  clustewr on the especified es_endpoint bellow 
#  using the elasticsearch-hadoop connector. 
# 
#  You can specify any name for your index, or create multiple indexex with different 
#  data. The driver will auto create the index (see line 75). 
#  The index format is "name/type". For more information about ElasticSearch indexes and type see:
#  https://www.elastic.co/blog/index-vs-type
#  For more information on the usage of the elasticsearch-hadoop connector see:
#  https://www.elastic.co/guide/en/elasticsearch/hadoop/current/configuration.html 
#  

es_index = "main-index/transactions"

DataFrame.write.mode("overwrite").format("org.elasticsearch.spark.sql").\
        option("es.resource", "index/type").\
        option("es.net.http.auth.user",args['es_user']).\
        option("es.net.http.auth.pass",args['es_pass']).\
        option("es.nodes", args['es_endpoint']).\
        option("es.port", 443).\
        option("es.nodes.wan.only", True).\
        option("es.index.auto.create", True).\
        option("es.resource", es_index).\
        option("es.mapping.id", "sequence_number").\
        option("es.write.operation", "upsert").\
        save()

print("Moved records: ", DataFrame.count())
print("Total records: ", DataFrame.count())

job.commit()
