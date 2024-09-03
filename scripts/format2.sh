#!/bin/bash

input_file="$1"

while IFS= read -r line; do
    name=$(echo "$line" | awk -F'/' '{print $2}' | awk -F' ' '{print $1}')
    echo "$name"
    list_part=$(echo "$line" | grep -oP '\[.*\]' | sed 's/^\[\(.*\)\]$/\1/')
    IFS=',' read -r -a array <<< "$list_part"

    for item in "${array[@]}"; do
        item=$(echo "$item" | sed 's/^"\(.*\)"$/\1/')
        if [[ "$item" == SQS* ]]; then
            echo "- $item"
        fi
    done
    if [ "$filtered_items" = true ]; then
        echo
    fi

done < "$input_file"

