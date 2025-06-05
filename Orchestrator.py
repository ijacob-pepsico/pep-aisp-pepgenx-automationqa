import subprocess
import csv
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to read API details from a CSV file
def read_api_details(csv_file):
    api_details = []
    try:
        with open(csv_file, encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Check if 'API Name' key exists and is not empty
                if row.get('API Name'):
                    api_details.append({
                        'API Name': row['API Name'],
                        'API Collection Path': row.get('API Collection Path', ''),
                        'API Data File Path': row.get('API Data File Path', ''),
                        'API Environment Path': row.get('API Environment Path', '')
                    })
                else:
                    logging.error("API Name is missing or empty in the CSV file.")
                    return []
    except FileNotFoundError:
        logging.error(f"CSV file not found: {csv_file}")
        return []
    return api_details

# Function to run Newman command
def run_newman(api, folder_path):
    if not os.path.exists(api['API Collection Path']):
        return f"API Collection Path not found for {api['API Name']}"
    
    # Create the reports directory if it doesn't exist
    os.makedirs(folder_path, exist_ok=True)
    
    # Format the report name
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    report_name = f"TestReport_{api['API Name']}_{timestamp}.html"
    report_path = os.path.join(folder_path, report_name)
    
    # Construct the Newman command with the report option
    newman_command = [
        "npx", "newman", "run", api['API Collection Path'], "-k", 
        "-r", "htmlextra", "--reporter-htmlextra-export", report_path, 
        "--timeout-request", "15000", "--disable-unicode", 
        "--export-environment", "/dev/null", "--export-globals", "/dev/null"
    ]
    if api['API Data File Path']:
        if not os.path.exists(api['API Data File Path']):
            return f"API Data File Path not found for {api['API Name']}"
        newman_command.extend(["-d", api['API Data File Path']])
    if api['API Environment Path']:
        if not os.path.exists(api['API Environment Path']):
            return f"API Environment Path not found for {api['API Name']}"
        newman_command.extend(["-e", api['API Environment Path']])
    
    logging.info(f"Executing Newman command: {' '.join(newman_command)}")
    result = subprocess.run(newman_command, shell=False)
    if result.returncode != 0:
        return f"Newman command failed for {api['API Name']}"
    return f"Newman command executed successfully for {api['API Name']}"

# Read API details from the CSV file (update the file path accordingly)
csv_file_path = os.getenv('CSV_FILE_PATH', 'api_details.csv')
api_details = read_api_details(csv_file_path)
folder_path = os.getenv('REPORTS_FOLDER', 'reports')

# Exit the script if no API details are found
if not api_details:
    exit()

# Print final message to console
messages = []
for api in api_details:
    message = run_newman(api, folder_path)
    if message:
        messages.append(f"{api['API Name']} : {message}")

logging.info("Execution Status:")
for msg in messages:
    logging.info(msg)