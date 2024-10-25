#!/usr/bin/env python3

import datetime
import os
import platform
import random
import subprocess
import sys

# Check the current OS (some functions are OS dependent)
system = platform.system()


def list_directories(root_dir: str):
    """
    Lists all subdirectories of the speficied directory
    Input: starting directory to search
    Return: list of all subdirectory paths
    """
    dirs = []
    with os.scandir(root_dir) as scan:
        for entry in scan:
            if not entry.name.startswith(".") and entry.is_dir():
                dirs.append(entry.path)
                sub_dirs = list_directories(entry.path)
                dirs.extend(sub_dirs)
    return dirs


def list_files(root_dir: str):
    """
    Lists all files of the speficied directory
    Input: starting directory to search
    Return: list of all file paths
    """
    files = []
    with os.scandir(root_dir) as scan:
        for entry in scan:
            if not entry.name.startswith(".") and entry.is_file():
                files.append(entry.path)
    return files


def rename_file(path: str, name: str, extension: str):
    """
    Renames the specified file to the specified name
    Input: path to file, name to rename file to
    Return: none
    """
    # Split path for removal of file name
    split_path = path.split("/")
    folder = ""
    for i in range(len(split_path) - 1):
        # Concatenate the folder path until reaching the filename
        folder += split_path[i] + "/"
    # Call Bash command to rename file
    os.system(f"mv {path} {folder}{name}.{extension}")


def move_file_up_one_level(path: str):
    """
    Moves speficied file into parent directory
    Input: path to file
    Return: none
    """
    split_path = path.split("/")
    new_directory = ""
    current_dir = len(split_path) - 2
    for i in range(len(split_path)):
        if i != current_dir and i != len(split_path) - 1:
            # Build the path to the parent directory
            new_directory += split_path[i] + "/"
        elif i != current_dir:
            new_directory += split_path[i]
    os.system(f"mv -n {path} {new_directory}")


def display_timestamp(file: str):
    """
    Displays the creation date and time of the specified file
    Input: path to file
    Return: formatted file creation date and time as str
    """
    # Get current OS (no Windows support since I don't have a machine for testing)
    system = platform.system()
    fmt = "awk '{print strftime(\"%Y-%m-%d %H:%M:%S\")}'"
    if system == "Linux":
        return subprocess.getoutput(f"stat -c %W {file} | {fmt}")
    if system == "Darwin":
        return subprocess.getoutput(f'stat -f "%SB" -t "%Y-%m-%d %H:%M:%S" {file}')


def remove_empty_directories(root_dir: str):
    """
    Scans subdirectories in specified path and removes the subdirectory if empty
    Input: path to starting directory
    Return: none
    """
    dirs = []
    # Scan for all subdirectories
    with os.scandir(root_dir) as scan:
        for entry in scan:
            if not entry.name.startswith(".") and entry.is_dir():
                dirs.append(entry.path)
                remove_empty_directories(entry.path)
    for dir in dirs:
        # Run ls command and capture output
        output = subprocess.getoutput(f"ls {dir}")
        # If the output is empty
        if output == "":
            # Remove the directory
            os.system(f"rm -df {dir}")


def backdate_system_date():
    """
    Changes system date to a random date in the past 10 days
    Input: none
    Return: none
    """
    i = random.randrange(1, 10, 1)
    if system == "Linux":
        os.system("sudo timedatectl set-ntp 0")
        os.system(f"sudo date -s '{i} days ago")
    if system == "Darwin":
        now = datetime.datetime.now()
        now = datetime.datetime.timetuple(now)
        os.system("sudo systemsetup -setusingnetworktime off")
        os.system(
            f"sudo date {now.tm_mon}{now.tm_mday - i}{now.tm_hour}{now.tm_min}{now.tm_year}"
        )


def reset_system_date():
    """
    Resets system date to automatic
    Input: none
    Return: none
    """
    if system == "Linux":
        os.system("sudo timedatectl set-ntp 1")
    if system == "Darwin":
        os.system("sudo systemsetup -setusingnetworktime on")


def change_creation_datetime(file: str):
    """
    Updates creation date of specified file
    Input: file to update
    Return: none
    """
    os.system(f"cp {file} {file}.backup")
    os.system(f"rm {file}")
    os.system(f"cp {file}.backup {file}")
    os.system(f"rm {file}.backup")


def schedule_program():
    """
    Prompts user for entry and creates a crontab entry based on the user entry
    Input: none
    Return: none
    """
    # Get the current user
    username = subprocess.getoutput("whoami")
    username = username.replace(" ", "\ ")
    # Get filepath for this script
    file_path = os.path.realpath(__file__)
    # Create path to venv (assumes venv created in conventional location)
    split_path = file_path.split("/")
    venv_path = ""
    log_path = ""
    for i in range(len(split_path) - 1):
        venv_path += split_path[i] + "/"
        log_path += split_path[i] + "/"
    venv_path += "venv/bin/python"
    log_path += "log.txt"
    venv_path = venv_path.replace(" ", "\ ")
    file_path = file_path.replace(" ", "\ ")
    log_path = log_path.replace(" ", "\ ")

    # Get user input for schedule frequency
    freq = input(
        "This program can be set to run on a schedule.\nEnter 1 to run weekly\nEnter 2 to run every 30 seconds\nEnter any other key to bypass scheduling: "
    )
    # Check crontab file to see if program is already scheduled
    cron = subprocess.getoutput("crontab -l")
    # Set the correct path for the crontab based on OS
    cron_path = ""
    if system == "Linux":
        cron_path = f"/var/spool/cron/crontabs/{username}"
    if system == "Darwin":
        cron_path = f"/usr/lib/cron/tabs/{username}"

    if freq == "1" and cron.find("midterm.py") == -1:
        # Schedule the script to run once per week at midnight on Sunday
        subprocess.run(
            f'echo "0 0 * * 0 {venv_path} {file_path} CRON >> {log_path}" | sudo tee -a {cron_path} > /dev/null',
            shell=True,
        )
    elif freq == "1" and cron.find("midterm.py") > 0:
        print("Already scheduled at this frequency")

    if freq == "2" and (cron.find("midterm.py") == -1 or cron.find("* * * * *") == -1):
        # Max cron frequency is every minute, so we need to create two entries
        # and offset them by 30 seconds to make it run more frequently
        subprocess.run(
            f'echo "* * * * * {file_path} CRON >> {log_path} 2>&1" | sudo tee -a {cron_path} > /dev/null',
            shell=True,
        )
        subprocess.run(
            f'echo "* * * * * (sleep 30 ; {file_path} CRON >> {log_path} 2>&1)" | sudo tee -a {cron_path} > /dev/null',
            shell=True,
        )


def main():
    # Generate a list of subdirectories
    dirs = list_directories("data")
    for dir in dirs:
        print(dir)
        # Get a list of files in the current directory
        files = list_files(dir)
        # If the list is not empty
        if files != []:
            # Move each file to its parent folder
            for file in files:
                print(f"File: {file} created on: {display_timestamp(file)}")
                move_file_up_one_level(file)

    # Remove any empty directories left after moving files
    remove_empty_directories("data")

    # Get a new listing of directories
    dirs = list_directories("data")
    for dir in dirs:
        # Get a list fo files in the current directory
        files = list_files(dir)
        # If the list if not empty
        if files != []:
            # Sequentially rename each file and change its extension to csv
            for index, file in enumerate(files):
                rename_file(file, index + 1, "csv")

    # Get a new listing of directories
    dirs = list_directories("data")
    backdate_system_date()
    for dir in dirs:
        # Get a list fo files in the current directory
        files = list_files(dir)
        # If the list if not empty
        if files != []:
            # Change the creation date for each file
            for file in files:
                change_creation_datetime(file)
    reset_system_date()

    # Generate a list of subdirectories
    dirs = list_directories("data")
    for dir in dirs:
        print(dir)
        # Get a list of files in the current directory
        files = list_files(dir)
        # If the list is not empty
        if files != []:
            # Print the new altered timestamps
            for file in files:
                print(f"File: {file} created on: {display_timestamp(file)}")


if __name__ == "__main__":
    main()
    # if len(sys.argv) <= 1 or sys.argv[1] != "CRON":
    #     schedule_program()
    # else:
    #     with open("log.txt", "a") as log:
    #         log.write(f"Ran via cron on {datetime.datetime.now()}\n")
