import json
import sys

# Get the file name from the command-line argument
if len(sys.argv) < 2:
    print("Please provide a file name.")
    sys.exit(1)
file_name = sys.argv[1]

# Open the JSON file and load its contents
with open(file_name, 'r') as f:
    data = json.load(f)

# Convert the data to a JSON-formatted string
json_string = json.dumps(data)

# Print the JSON string
print("\n" + json_string + "\n")
