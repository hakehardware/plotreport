import argparse
import requests
import platform
import uuid
import json
import cpuinfo
from datetime import datetime
import time
import subprocess


class Parser:
    @staticmethod
    def parse_docker(log_file):
        indexes = []
        times = []
        sectors = 0

        for line in log_file:
            log_entry = json.loads(line)
            log_message = log_entry["log"]
            log_time = log_entry["time"].split(".")[0]
            log_time = datetime.strptime(log_time, "%Y-%m-%dT%H:%M:%S")

            if "Plotting sector" in log_message:

                disk_index = log_message.split("disk_farm_index=")[1].split("}")[0]
                if disk_index not in indexes:
                    indexes.append(disk_index)

                times.append(log_time)
                sectors += 1

        oldest_datetime = min(times)
        newest_datetime = max(times)
        time_difference = (newest_datetime - oldest_datetime).total_seconds() / 60

        plot_time = time_difference / len(times)
        return {
            "plot_time": round(plot_time, 2),
            "disks": len(indexes),
            "sectors": sectors,
        }

    @staticmethod
    def parse_log_file(log_file):
        indexes = []
        times = []
        sectors = 0

        for line in log_file:
            if "Plotting sector" in line:
                log_time = line.split(" ")[0].split(".")[0]
                log_time = datetime.strptime(log_time, "%Y-%m-%dT%H:%M:%S")

                log_message = line.split("  ")[1]
                disk_index = log_message.split("disk_farm_index=")[1].split("}")[0]

                if disk_index not in indexes:
                    indexes.append(disk_index)

                times.append(log_time)
                sectors += 1

        oldest_datetime = min(times)
        newest_datetime = max(times)

        time_difference = (newest_datetime - oldest_datetime).total_seconds() / 60

        plot_time = time_difference / len(times)
        return {
            "plot_time": round(plot_time, 2),
            "disks": len(indexes),
            "sectors": sectors,
        }

    @staticmethod
    def parse_acli(log_file):
        indexes = []
        times = []
        sectors = 0

        for line in log_file:
            if "Plotting sector" in line:
                log_time = line.split(" ")[5].split(".")[
                    0
                ]  # Select the 6th part and remove the fractional seconds
                log_time = datetime.strptime(log_time, "%Y-%m-%dT%H:%M:%S")

                log_message = line.split("  ")[1]
                disk_index = log_message.split("disk_farm_index=")[1].split("}")[0]

                if disk_index not in indexes:
                    indexes.append(disk_index)

                times.append(log_time)
                sectors += 1

        oldest_datetime = min(times)
        newest_datetime = max(times)

        time_difference = (newest_datetime - oldest_datetime).total_seconds() / 60

        plot_time = time_difference / len(times)
        return {
            "plot_time": round(plot_time, 2),
            "disks": len(indexes),
            "sectors": sectors,
        }

    @staticmethod
    def get_system_info():
        # Get OS information
        os_info = platform.system() + " " + platform.release()

        # Get CPU information
        info = cpuinfo.get_cpu_info()
        cpu_brand = info.get("brand_raw", "Unknown CPU Brand")

        return {"cpu": cpu_brand, "os": os_info}


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


def run(log_location, file_type, user_unit, log_lines):
    # Get Plotting Times
    plotting_data = None
    platform = None

    if log_location == "" and user_unit != "":
        process = subprocess.Popen(
            ["journalctl", "--user-unit", user_unit, "-n", log_lines],
            stdout=subprocess.PIPE,
        )
        log_file = process.stdout.read().decode("utf-8").split("\n")
    else:
        log_file = open(log_location, "r", encoding="utf-8")

    if file_type == 0:
        plotting_data = Parser.parse_docker(log_file)
        platform = "Docker"
    elif file_type == 1:
        plotting_data = Parser.parse_log_file(log_file)
        platform = "Space Acres"
    elif file_type == 2:
        plotting_data = Parser.parse_acli(log_file)
        platform = "ACLI"
    else:
        raise ValueError(f"File Type of {file_type} does not match options.")

    # Get System Info
    system_info = Parser.get_system_info()

    # Display Data

    # Prompt User
    submit_uuid = uuid.uuid4()

    submission_time_utc = time.time()

    if plotting_data and system_info:
        print(
            f"""
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

    """
        )
        user_input = input("Would you like to continue? (Y/n): ").strip().lower()

        if user_input in ["", "y", "yes"]:
            print("submitting")

            # Submit Data
            submit_data(
                {
                    "uid": f"{submit_uuid}",
                    "os": system_info["os"],
                    "cpu": system_info["cpu"],
                    "disks": str(plotting_data["disks"]),
                    "speed": str(plotting_data["plot_time"]),
                    "platform": platform,
                    "sectors": str(plotting_data["sectors"]),
                    "submission_time_utc": str(submission_time_utc),
                }
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process command line arguments.")
    parser.add_argument(
        "-l", "--log", help="Path to a log file", type=str, required=False, default=""
    )
    parser.add_argument(
        "-t", "--type", help="0-Docker, 1-Space Acres, 2-ACLI", type=int, required=True
    )
    parser.add_argument(
        "-u",
        "--userunit",
        help="Name of user unit to pull logs for",
        type=str,
        required=False,
        default="",
    )
    parser.add_argument(
        "-n",
        "--loglines",
        help="Journalctl lines to parse",
        type=str,
        required=False,
        default="",
    )
    args = parser.parse_args()

    run(args.log, args.type, args.userunit, args.loglines)
