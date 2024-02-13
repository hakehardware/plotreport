import argparse
import requests
import platform
import uuid
import json
import cpuinfo
from datetime import datetime


class Parser:
    @staticmethod
    def parse_docker(log_location):
        indexes = []
        times= []
        sectors=0

        with open(log_location, 'r') as log_file:
            for line in log_file:
                log_entry = json.loads(line)
                log_message = log_entry["log"]
                log_time = log_entry['time'].split('.')[0]
                log_time = datetime.strptime(log_time, "%Y-%m-%dT%H:%M:%S")

                if "Plotting sector" in log_message:

                    disk_index = log_message.split("disk_farm_index=")[1].split("}")[0]
                    if disk_index not in indexes:
                        indexes.append(disk_index)

                    times.append(log_time)
                    sectors+=1

            oldest_datetime = min(times)
            newest_datetime = max(times)
            # print(f'Oldest Time: {oldest_datetime}')
            # print(f'Newest Time: {newest_datetime}')
            # print(f'Total Sectors: {len(times)}')
            # print(f'Total Disks: {len(indexes)}')

            time_difference = (newest_datetime - oldest_datetime).total_seconds() / 60
            # print(f'Total Time Difference: {time_difference}')

            plot_time = time_difference/len(times)
            return {"plot_time": round(plot_time,2), "disks": len(indexes), "sectors": sectors}

    @staticmethod
    def parse_log_file(log_location):
        indexes = []
        times= []
        sectors=0

        with open(log_location, 'r', encoding='utf-8') as log_file:
            for line in log_file:
                if "Plotting sector" in line:
                    log_time = line.split(' ')[0].split('.')[0]
                    log_time = datetime.strptime(log_time, "%Y-%m-%dT%H:%M:%S")


                    log_message = line.split('  ')[1]
                    disk_index = log_message.split("disk_farm_index=")[1].split("}")[0]


                    if disk_index not in indexes:
                        indexes.append(disk_index)

                    times.append(log_time)
                    sectors+=1

            oldest_datetime = min(times)
            newest_datetime = max(times)
            # print(f'Oldest Time: {oldest_datetime}')
            # print(f'Newest Time: {newest_datetime}')
            # print(f'Total Sectors: {len(times)}')
            # print(f'Total Disks: {len(indexes)}')

            time_difference = (newest_datetime - oldest_datetime).total_seconds() / 60
            # print(f'Total Time Difference: {time_difference}')

            plot_time = time_difference/len(times)
            return {"plot_time": round(plot_time,2), "disks": len(indexes), "sectors": sectors}

    @staticmethod
    def parse_acli(log_location):
        print('Advanced CLI is currently not supported.')
        return None

    @staticmethod
    def get_system_info():
        # Get OS information
        os_info = platform.system() + " " + platform.release()
        
        # Get CPU information
        info = cpuinfo.get_cpu_info()
        cpu_brand = info.get('brand_raw', 'Unknown CPU Brand')
        
        return {
            "cpu": cpu_brand,
            "os": os_info
        }

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

def run(log_location, file_type):
    # Get Plotting Times
    plotting_data = None
    platform = None

    if file_type == 0:
        plotting_data = Parser.parse_docker(log_location)
        platform = "Docker"
    elif file_type == 1:
        plotting_data = Parser.parse_log_file(log_location)
        platform = "Space Acres"
    elif file_type == 2:
        plotting_data = Parser.parse_log_file(log_location)
        platform = "ACLI"
    else:
        raise ValueError(f'File Type of {file_type} does not match options.')
    
    # Get System Info
    system_info = Parser.get_system_info()

    # Display Data

    # Prompt User
    submit_uuid = uuid.uuid4()

    submission_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if plotting_data and system_info:
        print(f'''
    Only the below data will be sent to the plotreport.hakedev.com:
              
    ======= System Info ===========
    Operating System: {system_info['os']}
    CPU: {system_info['cpu']}
    Platform: {platform}

    =======Plotting Data===========
    Plot Time: {plotting_data['plot_time']}
    Disks: {plotting_data['disks']}
    Sectors: {plotting_data['sectors']}

    Submission UUID: {submit_uuid}

    ''')
        user_input = input("Would you like to continue? (Y/n): ").strip().lower()

        if user_input in ['', 'y', 'yes']:
            print('submitting')

            # Submit Data
            submit_data({
                "uid": f'{submit_uuid}', 
                "os": system_info['os'],
                "cpu": system_info['cpu'],
                "disks": str(plotting_data['disks']),
                "speed": str(plotting_data['plot_time']),
                "platform": platform,
                "sectors": str(plotting_data['sectors']),
                "submission_time": submission_time
            })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process command line arguments.")
    parser.add_argument("-l", "--log", help="Path to a log file", type=str, required=True)
    parser.add_argument("-t", "--type", help="0-Docker, 1-Space Acres, 2-ACLI", type=int, required=True)
    args = parser.parse_args()

    run(args.log, args.type)