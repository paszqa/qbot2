#!/bin/bash

# Define start and end dates
start_date="2023-12-31"
end_date="2024-03-01"

# Convert start and end dates to timestamps
start_timestamp=$(date -d "$start_date" +%s)
end_timestamp=$(date -d "$end_date" +%s)

# Iterate over dates and execute the command
current_timestamp=$start_timestamp
while [ "$current_timestamp" -le "$end_timestamp" ]; do
    current_date=$(date -d "@$current_timestamp" "+%Y-%m-%d")
    echo "Processing activity for $current_date"
    python3 processActivity.py "$current_date"
    # Increment timestamp by one day (86400 seconds)
    current_timestamp=$((current_timestamp + 86400))
done
