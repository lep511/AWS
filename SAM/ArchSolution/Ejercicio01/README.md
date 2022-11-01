# Building a Proof of Concept for a Serverless Solution

This exercise provides you with instructions for how to build a proof of concept for a serverless solution in the AWS Cloud.

Suppose you have a customer that needs a serverless web backend hosted on AWS. The customer sells cleaning supplies and often sees spikes in demand for their website, which means that they need an architecture that can easily scale in and out as demand changes. The customer also wants to ensure that the application has decoupled application components.

The following architectural diagram shows the flow for the serverless solution that you will build:

![Diagram](https://aws-tc-largeobjects.s3.us-west-2.amazonaws.com/DEV-AWS-MO-Architecting/images/exercise-1.png)

In this architecture, you will use a REST API to place a database entry in the Amazon SQS queue. Amazon SQS will then invoke the first Lambda function, which inserts the entry into a DynamoDB table. After that, DynamoDB Streams will capture a record of the new entry in a database and invoke a second Lambda function. The function will pass the database entry to Amazon SNS. After Amazon SNS processes the new record, it will send you a notification through a specified email address.

In this exercise, you will learn how to do the following:

* Create IAM policies and roles to follow best practices of working in the AWS Cloud.
* Create a DynamoDB table to store data.
* Create an Amazon SQS queue to receive, store, and send messages between software components.
* Create Lambda functions and set up triggers to invoke actions in different AWS services.
* Enable DynamoDB Streams to capture modifications in the database table.
* Configure Amazon SNS to receive email or text notifications.
* Create a REST API to insert data into a database.