#!/bin/sh
echo "##### Deploy SAM ArchSolution 02 #####"
echo " "
echo "  1. Deploy App with API Gateway and Athena"
echo "  2. Deploy App without API Gateway"
echo "  3. Deploy App without Athena"
echo "  4. Deploy App without API Gateway and Athena"
echo "  5. Generate sample data to Kinesis Firehose"
echo " "
read -p "Enter an option: " option
success=0

case $option in
  1)
    echo " " && echo "Deploying App with API Gateway and Athena"
    sam build
    sam deploy --template-file template.yaml --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM --guided
    success=1
    ;;
  2)
    echo " " && echo "Deploying App without API Gateway"
    sam build
    sam deploy --template-file template_without_apirest.yaml --capabilities CAPABILITY_NAMED_IAM --guided
    success=1
    ;;
  3)
    echo " " && echo "Deploying App without Athena"
    sam build
    sam deploy --template-file template_without_athena.yaml --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM --guided
    success=1
    ;;
  4)
    echo " " && echo "Deploying App without API Gateway and Athena"
    sam build
    sam deploy --template-file template_without_all.yaml --capabilities CAPABILITY_NAMED_IAM --guided
    success=1
    ;;
  5)
    echo " "
    success=1
    ;;
  *)
    echo " " && echo "Invalid option"
    ;;
esac

if [ $success -eq 1 ]; then
    read -p "Enter the number of events: " events
    python generate_track.py --repeat $events
fi
