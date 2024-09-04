#!/bin/bash

input_file="$1"
SQS_ARRAY=()
declare -A key_value_array
while IFS= read -r line; do
    name=$(echo "$line" | awk -F'/' '{print $2}' | awk -F' ' '{print $1}')
    echo "$name:"
    list_part=$(echo "$line" | grep -oP '\[.*\]' | sed 's/^\[\(.*\)\]$/\1/')
    IFS=',' read -r -a array <<< "$list_part"

    for item in "${array[@]}"; do
        item=$(echo "$item" | sed 's/^"\(.*\)"$/\1/')
        if [[ "$item" == SQS* && "$item" != *http* && "$item" != *REGION* && "$item" != *PREFIX* ]]; then
	    key=$(echo "$item" | cut -d '=' -f 1)
	    value=$(echo "$item" | cut -d '=' -f 2)
#	    key_value_array["$key"]="$value"
            SQS_ARRAY+=(\""$item\"")
        fi
    done
#  for key in "${!key_value_array[@]}"; do
#    echo "${key}:${key_value_array[$key]}"
#  done
    put_items_together=$(IFS=','; echo "${SQS_ARRAY[*]}")
    put_items_together=$(echo "$put_items_together" |sed 's/,/ , /g')
    echo "  SQS: [${put_items_together}]"
#    if [ "$filtered_items" = true ]; then
#        echo
#    fi

done < "$input_file"
