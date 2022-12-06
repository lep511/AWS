# Building a Proof of Concept for Data Analytics

This exercise provides you with instructions for how to build a data analytics solution.

This week, you will design an architecture for a customer who needs an analytics solution to ingest, store, and visualize clickstream data. The customer is a restaurant owner who wants to derive insights for all menu items that are ordered in their restaurant. Because the customer has limited staff for running and maintaining this solution, you will build a proof of concept by using managed services on AWS.

The following architectural diagram shows the flow that you will follow.
<br><br>
![Image](https://aws-tc-largeobjects.s3.us-west-2.amazonaws.com/DEV-AWS-MO-Architecting/images/exercise-2.png)

In this architecture, you use API Gateway to ingest clickstream data. Then, the Lambda function transforms the data and sends it to Kinesis Data Firehose. The Firehose delivery stream places all files in Amazon S3. Then, you use Amazon Athena to query the files. Finally, you use Amazon QuickSight to transform data into graphics.

In this exercise, you will learn how to do the following:

* Create IAM policies and roles to follow the best practices of working in the AWS Cloud.
* Create the object storage S3 bucket to store clickstream data.
* Create the Lambda function for Amazon Kinesis Data Firehose to transform data.
* Create a Kinesis Data Firehose delivery stream to deliver real-time streaming data to Amazon S3.
* Create a REST API to insert data.
* Create an Amazon Athena table to view the obtained data.
* Create Amazon QuickSight dashboards to visualize data.

## Execution

`bash deploy-app.sh`