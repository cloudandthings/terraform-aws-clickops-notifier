#!/bin/bash

set -e

TARGETS=$(jq -c '.include[]' build_targets.json)

while IFS= read -r line; do
    NAME=$(echo "$line" | jq -r '.name')
    RUNTIME=$(echo "$line" | jq -r '.runtime')
    bash ./build_one.sh $NAME $RUNTIME
done <<< "$TARGETS"
