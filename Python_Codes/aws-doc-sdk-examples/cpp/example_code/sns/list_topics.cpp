/*
   Copyright 2010-2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
   This file is licensed under the Apache License, Version 2.0 (the "License").
   You may not use this file except in compliance with the License. A copy of
   the License is located at
    http://aws.amazon.com/apache2.0/
   This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied. See the License for the
   specific language governing permissions and limitations under the License.
*/

#include <aws/core/Aws.h>
#include <aws/sns/SNSClient.h>
#include <aws/sns/model/ListTopicsRequest.h>
#include <aws/sns/model/ListTopicsResult.h>
#include <iostream>

/**
 * Lists topics - demonstrates how to retrieve a list of Amazon SNS topics.
 */

int main(int argc, char ** argv)
{
  if (argc != 1)
  {
    std::cout << "Usage: list_topics" << std::endl;
    return 1;
  }
  // snippet-start:[sns.cpp.list_topics.code]
  Aws::SDKOptions options;
  Aws::InitAPI(options);
  {
    Aws::SNS::SNSClient sns;

    Aws::SNS::Model::ListTopicsRequest lt_req;

    auto lt_out = sns.ListTopics(lt_req);

    if (lt_out.IsSuccess())
    {
      std::cout << "Topics list:" << std::endl;
      for (auto const &topic : lt_out.GetResult().GetTopics())
      {
        std::cout << "  * " << topic.GetTopicArn() << std::endl;
      }
    }
    else
    {
      std::cout << "Error listing topics " << lt_out.GetError().GetMessage() <<
        std::endl;
    }
  }

  Aws::ShutdownAPI(options);
  // snippet-end:[sns.cpp.list_topics.code]
  return 0;
}
