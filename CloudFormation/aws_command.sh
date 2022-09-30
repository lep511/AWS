# export template_file="cloud_formation_sample.yaml"
# export mystack="name-stack"
aws cloudformation create-stack \
  --stack-name $mystack \
  --template-body file://$template_file