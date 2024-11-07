#!/bin/bash

display_help() {
    echo "Usage: $0 <start_time> <app_name> <exit_code> <schedule>"
    echo
    echo "Parameters:"
    echo "  start_time  - Start time in epoch format (e.g., \$(date +%s))"
    echo "  app_name    - Name of the cronjob"
    echo "  exit_code   - Value to be posted as metric"
    echo "  schedule    - Cron schedule"
    echo
    echo "Example:"
    echo "  $0 1609459200 cronjob_name 12345 '*/5|*|*|*|*'"
    exit 1
}

# Check if the required number of arguments are provided
if [ $# -lt 4 ]; then
    echo "Error: Not enough arguments provided."
    display_help
fi

start_time=$1
app_name=$2
value=$3
schedule=$4
#host=$5
duration_sec=$(( $(date +\%s) - $start_time ))
metric_name=cron_execution
host=$(hostname)

#echo "1 ${start_time}, 2 ${app_name}, 3 ${value}, 4 ${schedule}, 5 ${host} -> duration_sec = ${duration_sec}"

curl -s -X POST http://localhost:5902/v1/post_metric \
    -H "Content-Type: application/json" \
    -d "{\"app_name\": \"${app_name}\", \"metric_name\": \"${metric_name}\", \"value\": ${value}, \"schedule\": \"${schedule}\", \"host\": \"${host}\", \"duration_sec\": ${duration_sec}}" > /dev/null
