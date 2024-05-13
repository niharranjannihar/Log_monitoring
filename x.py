import re
import requests
import json
import os
import yaml

count = 1
merged_output = ""  # Initialize an empty string to store the merged output
log_types = ["INFO", "ERROR", "WARN", "DEBUG"]
with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

service = config['service']
serviceInstance = config['serviceInstance']
layer = config['layer']
traceId = config['traceId']
spanId = config['spanId']
source_log_path = config['source_log_path']
traceSegmentId = config['traceSegmentId']
controller_host = config['controller-host']


print (service)

def extract_timestamp(log_line):
    # Regular expression pattern to extract timestamp
    timestamp_pattern = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'
    match = re.search(timestamp_pattern, log_line)
    if match:
        return match.group(1)
    return None


def compare_logs(log1_path, source_log_path):
    global count, merged_output  # Declare count and merged_output as global variables

    with open(log1_path, 'r') as log1, open(source_log_path, 'r') as log2:
        log1_lines = log1.readlines()
        log2_lines = log2.readlines()

    log1_index = 0
    log2_index = 0

    while log1_index < len(log1_lines) and log2_index < len(log2_lines):
        log1_line = log1_lines[log1_index].strip()
        log2_line = log2_lines[log2_index].strip()

        if log1_line == log2_line:
            log1_index += 1
            log2_index += 1
        else:
            # Add the line from source_log_path to merged_output
            x = log2_line
            log2_index += 1
            count += 1  # Increment count
            merged_output += x + "\n"  # Append x to merged_output with a newline

    # Append remaining logs from log2 (source_log_path) if any
    while log2_index < len(log2_lines):
        x = log2_lines[log2_index].strip()
        log2_index += 1
        count += 1  # Increment count
        merged_output += x + "\n"  # Append x to merged_output with a newline

    # If log2 has ended before matching timestamps are found
    if log2_index == len(log2_lines):
        print("Log 2 ended before matching timestamps were found.")



if __name__ == "__main__":
    log1_path = "copylog.txt"  # Path to the first log file
    #source_log_path = "log.txt"  # Path to the second log file
    compare_logs(log1_path, source_log_path)
    log_pattern = r'\b\d{4}-\d{2}-\d{2}\b'
    matches = re.findall(log_pattern, merged_output)

    if matches:
        for match in matches:
            print('New timestamp arrises :', match)
    else:
        print("No matches found.")
    # print(merged_output)
    v = 0
    for line_num, line in enumerate(merged_output.split('\n'), 1):
        # Check if the line matches the timestamp pattern
        match = extract_timestamp(line)
        if match:

            # If a match is found, create a new file with the line number as the filename
            filename = f"output_{v}.log"
            with open(filename, 'a') as file:
                # Append the line to the file
                file.write(line + '\n')
                v += 1
        else:
            # If no match is found, append the line to the last created file
            if filename:
                with open(filename, 'a') as file:
                    file.write(line + '\n')

    log_data = []

    # Loop through the log files
    for i in range(v):
        filename = f"output_{i}.log"
        with open(filename, "r") as f:
            # Read the content of the file
            content = f.read()
            json_data = json.dumps(content)
            if json_data:
                # Split the content by lines and process each line
                for line in content.split('\n'):
                    # Split each line into words
                    words = line.strip().split()
                    # Check if any word matches with log types
                    for log_type in words:
                        if log_type in log_types:
                            # Create the data dictionary inside this loop to associate each log entry with the correct log type
                            data = [
                                {
                                    "service": service,
                                    "serviceInstance": serviceInstance,
                                    "layer": layer,
                                    "traceContext": {
                                        "traceId": traceId,
                                        "spanId": spanId,
                                        "traceSegmentId": traceSegmentId
                                    },
                                    "tags": {
                                        "data": [
                                            {
                                                "key": "level",
                                                "value": log_type  
                                            },
                                            {
                                                "key": "logger",
                                                "value": "com.example.MyLogger"
                                            },
                                            {
                                                "key": "level",
                                                "value": source_log_path
                                            }
                                        ]
                                    },
                                    "body": {
                                        "text": {
                                            "text": content
                                        }
                                    }
                                }
                            ]
                            headers = {'Content-Type': 'application/json'}
                            url = f"http://{controller_host}:12800/v3/logs"
                            response = requests.post(url, json=data, headers=headers)
                            print(response.text)
                            print(response.status_code, response.reason)
                            print(data)
                            break  # Break the loop once a log_type is found
            else:
                print("Nothing changed.")
for i in range(v):
    os.remove(f"output_{i}.log")
print (merged_output)
with open("copylog.txt", "a") as copylog_file:
        copylog_file.write(merged_output)

# Insert the breakpoint for debugging
