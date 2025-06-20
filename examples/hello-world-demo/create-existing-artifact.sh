#!/bin/bash

SMO_URL="http://10.0.3.53:8000"
REGISTRY_URL="http://10.0.3.53:5000"

curl -X POST "$SMO_URL/project/test/graphs" \
     -H "Content-Type: application/json" \
     --data '{"artifact": "'$REGISTRY_URL'/test/hello-world-graph"}'
