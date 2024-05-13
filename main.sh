#!/bin/bash

service=$(yq e '.service' config.yml)
serviceInstance=$(yq e '.serviceInstance' config.yml)
layer=$(yq e '.layer' config.yml)
traceId=$(yq e '.traceId' config.yml)
spanId=$(yq e '.spanId' config.yml)
log_name=$(yq e '.log_name' config.yml)
traceSegmentId=$(yq e '.traceSegmentId' config.yml)
host=$(yq e '.controller-host' config.yml)
application_id=$(jq -Rs '.' log.txt)

log_types="INFO ERROR WARN DEBUG warning"
for log_type in $application_id; do
    if echo "$log_types" | grep -q -i "$log_type"; then
        break
    fi
done

logfile="log.txt"
count=1
x=""
while IFS= read -r line; do
    timestamp=$(echo "$line" | cut -d' ' -f1)
    if [[ $timestamp =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
        if ((count > 1)); then
            # Print the previous output file
            echo "Contents of output$((count - 1)).log:"
            cat "output$((count - 1)).log"
            echo "--------------------------------------"
        fi
        # Store the content of current output file into x before incrementing count
        x=$(cat "output$count.log")
        ((count++))
    fi
    echo "$line" >> "output$count.log"
done < "$logfile"

# Print the last output file if count is greater than 1
if ((count > 1)); then
    echo "Contents of output$((count - 1)).log:"
    cat "output$((count - 1)).log"
    echo "--------------------------------------"
fi

# Print the value of x
echo "Value of x: $x"

# Loop through the log files starting from output2.log
for ((i = 2; i < count+1; i++)); do
    cat "output$i.log"
    y=$(< "output$i.log")
    modified_y=$(jq -Rs '.' output$i.log)
    echo "$modified_y"
    payload='[{
    "service": "'"$service"'",
    "serviceInstance": "'"$serviceInstance"'",
    "layer":"'"$layer"'",
    "traceContext": {
      "traceId": "'"$traceId"'",
      "spanId": "0",
      "traceSegmentId": "'"$traceSegmentId"'"
    },
    "tags": {
      "data": [
        {
          "key": "level",
          "value": "'"$log_type"'"
        },
        {
          "key": "logger",
          "value": "com.example.MyLogger"
        },
        {
          "key": "level",
          "value": "'"$log_name"'"
        }
      ]
    },
    "body": {
      "text": {
        "text": '"$modified_y"'
      }
    }
  }]'

# Send the JSON payload using curl
curl -X POST -H "Content-Type: application/json" -d "$payload" http://$host:12800/v3/logs
    
done
