#!/bin/sh
echo "##### Deploy SAM ArchSolution 02 #####"
echo " "
echo "  1. Deploy App with API Gateway and Athena"
echo "  2. Deploy App without API Gateway"
echo "  3. Deploy App without Athena"
echo "  4. Deploy App without API Gateway and Athena"
echo "  5. Deploy template Kinesis Data Generator with Cognito"
echo " "
read -p "Enter an option: " option
success=0

case $option in
  1)
    echo " " && echo "Deploying App with API Gateway and Athena"
    read -p "Deploy guided (y/N)? " guided
    if [[ "$guided" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        sam build
        sam deploy --template-file template.yaml --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM --guided
    else
        sam build
        sam deploy --template-file template.yaml --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM
    fi
    success=1
    ;;
  2)
    echo " " && echo "Deploying App without API Gateway"
    read -p "Deploy guided (y/N)? " guided
    if [[ "$guided" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        sam build -t template_without_apirest.yaml
        sam deploy --template-file template_without_apirest.yaml --capabilities CAPABILITY_NAMED_IAM --guided
    else
        sam build -t template_without_apirest.yaml
        sam deploy --template-file template_without_apirest.yaml --capabilities CAPABILITY_NAMED_IAM
    fi
    success=1
    ;;
  3)
    echo " " && echo "Deploying App without Athena"
    read -p "Deploy guided (y/N)? " guided
    if [[ "$guided" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        sam build -t template_without_athena.yaml
        sam deploy --template-file template_without_athena.yaml --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM --guided
    else
        sam build -t template_without_athena.yaml
        sam deploy --template-file template_without_athena.yaml --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM
    fi
    success=1
    ;;
  4)
    echo " " && echo "Deploying App without API Gateway and Athena"
    read -p "Deploy guided (y/N)? " guided
    if [[ "$guided" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        sam build -t template_without_all.yaml
        sam deploy --template-file template_without_all.yaml --capabilities CAPABILITY_NAMED_IAM --guided
    else
        sam build -t template_without_all.yaml
        sam deploy --template-file template_without_all.yaml --capabilities CAPABILITY_NAMED_IAM
    fi
    success=1
    ;;
  5)
    echo " " && echo "Deploy the template Kinesis Data Generator with Cognito"
    sam build --template-file template_kinesis_data_generator.yaml --config-file kin_gen_samconfig.toml
    sam deploy --template-file template_kinesis_data_generator.yaml --capabilities CAPABILITY_NAMED_IAM --config-file kin_gen_samconfig.toml --guided
    success=0
    ;;
  *)
    echo " " && echo "Invalid option"
    ;;
esac

if [ $success -eq 1 ]; then
    read -p "Deploy the template Kinesis Data Generator (y/N)? " deploy_kdg
    if [[ "$deploy_kdg" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo " " && echo "Deploy the template Kinesis Data Generator with Cognito"
    sam build --template-file template_kinesis_data_generator.yaml --config-file kin_gen_samconfig.toml
    sam deploy --template-file template_kinesis_data_generator.yaml --capabilities CAPABILITY_NAMED_IAM --config-file kin_gen_samconfig.toml --guided
    fi
fi
