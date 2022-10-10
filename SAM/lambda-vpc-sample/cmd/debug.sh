#!/bin/bash
script_path=$(cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P)
sam local invoke \  
  --event ${script_path}/../test-event.json \  
  --template-file ${script_path}/../template.yaml