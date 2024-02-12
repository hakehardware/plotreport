import sys
import requests
import platform
import psutil
import uuid
import json
import cpuinfo

def analyze_log_file(file_path):
    """Analyze the log file and return analysis results."""
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            # Example analysis: count the number of lines in the log file
            line_count = len(lines)
            return {'line_count': line_count}
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        sys.exit(1)

def submit_data(data):
    """Submit the analyzed data to the server."""
    api_endpoint = "https://eox0s4p1ve.execute-api.us-west-2.amazonaws.com/prod/submit"
    try:
        response = requests.post(api_endpoint, json=data)
        if response.status_code == 200:
            print("Data submitted successfully.")
        else:
            print(f"Failed to submit data. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred while submitting data: {str(e)}")

def get_system_info():
    # Get OS information
    os_info = platform.system() + " " + platform.release()
    
    # Get CPU information
    info = cpuinfo.get_cpu_info()
    cpu_brand = info.get('brand_raw', 'Unknown CPU Brand')

    print("CPU Brand:", cpu_brand)
    print("Operating System:", os_info)
    
    return {
        "cpu": cpu_brand,
        "os": os_info
    }

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_log_file>")
        sys.exit(1) 
    
    system_info = get_system_info()

    print(json.dumps({
        "uid": f'{uuid.uuid4()}', 
        "os": system_info['os'],
        "cpu": system_info['cpu'],
        "disks": "4",
        "speed": "3.5"
    }, indent=4))

    # Ask the user if they want to submit the data
    user_input = input("Would you like to submit the data to the server? (Y/n): ").strip().lower()

    if user_input in ['', 'y', 'yes']:
        print('submitting')
        
        submit_data({
            "uid": f'{uuid.uuid4()}', 
            "os": system_info['os'],
            "cpu": system_info['cpu'],
            "disks": "4",
            "speed": "3.5"
        })
    else:
        print("Exiting without submitting data.")
        sys.exit(0)
