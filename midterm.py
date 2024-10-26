#!/usr/bin/env python3

"""
Filename: midterm.py

Description: A program to rename and organize files, modifiy creation date of files,
and optionally schedule processing via cron.

Authors: Adam Hough, Md Mahmudul Islam, Prakriti Thapa
"""

import datetime
import os
import platform
import random
import subprocess
import sys
import time

# Check the current OS (some functions are OS dependent)
system = platform.system()

global_count = 100


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
    file_exists = subprocess.getoutput(
        f"test -e {folder}{name}.{extension} && echo true || echo false"
    )
    if file_exists == "true":
        os.system(f"mv -n {path} {folder}{name}{name}.{extension}")
    else:
        os.system(f"mv -n {path} {folder}{name}.{extension}")


def move_file_up_one_level(path: str):
    """
    Moves speficied file into parent directory
    Input: path to file
    Return: none
    """
    global global_count
    split_path = path.split("/")
    new_directory = ""
    current_dir = len(split_path) - 2
    for i in range(len(split_path)):
        if i != current_dir and i != len(split_path) - 1:
            # Build the path to the parent directory
            new_directory += split_path[i] + "/"
        elif i != current_dir:
            new_directory += split_path[i]
    file_exists = subprocess.getoutput(
        f"test -e {new_directory} && echo true || echo false"
    )
    if file_exists == "true":
        new_path = new_directory.split(".")
        os.system(f"mv -n {path} {new_path[0]}{global_count}.{new_path[1]}")
        global_count += 1
    else:
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
        return subprocess.getoutput(f"stat -c %Y {file} | {fmt}")
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
            os.system(f"rm -rf {dir}")


def backdate_system_date():
    """
    Changes system date to a random date in the past 10 days
    Input: none
    Return: none
    """
    i = random.randrange(1, 10, 1)
    if system == "Linux":
        os.system("timedatectl set-ntp 0")
        now = datetime.datetime.now()
        now = datetime.datetime.timetuple(now)
        os.system(
            f'sudo date -s "{now.tm_year}-{now.tm_mon:02}-{(now.tm_mday - i):02} {now.tm_hour:02}:{now.tm_min:02}:{now.tm_sec:02}"'
        )
    if system == "Darwin":
        now = datetime.datetime.now()
        now = datetime.datetime.timetuple(now)
        os.system("sudo systemsetup -setusingnetworktime off 2> /dev/null")
        os.system(
            f"sudo date {now.tm_mon:02}{(now.tm_mday - i):02}{now.tm_hour:02}{now.tm_min:02}{now.tm_year}"
        )


def reset_system_date():
    """
    Resets system date to automatic
    Input: none
    Return: none
    """
    if system == "Linux":
        os.system("timedatectl set-ntp 1")
    if system == "Darwin":
        os.system("sudo systemsetup -setusingnetworktime on 2> /dev/null")


def change_creation_datetime(file: str):
    """
    Updates creation date of specified file
    Input: file to update
    Return: none
    """
    if system == "Linux":
        i = random.randrange(1, 10, 1)
        now = datetime.datetime.now()
        now = datetime.datetime.timetuple(now)
        dts = f"{now.tm_year}-{now.tm_mon:02}-{(now.tm_mday - i):02} {now.tm_hour:02}:{now.tm_min:02}:{now.tm_sec:02}"
        dt = datetime.datetime.strptime(dts, "%Y-%m-%d %H:%M:%S")
        timestamp = dt.timestamp()
        os.utime(file, (timestamp, timestamp))
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
    # Get filepath for this script
    file_path = os.path.realpath(__file__)
    split_path = file_path.split("/")
    log_path = ""
    for i in range(len(split_path) - 1):
        log_path += split_path[i] + "/"
    log_path += "log.txt"
    file_path = file_path.replace(" ", "\ ")
    log_path = log_path.replace(" ", "\ ")

    # Get user input for schedule frequency
    freq = input(
        "This program can be set to run on a schedule.\nEnter 1 to run weekly\nEnter 2 to run every 30 seconds\nEnter any other key to bypass scheduling: "
    )
    # Check crontab file to see if program is already scheduled
    cron = subprocess.getoutput("crontab -l")

    if freq == "1" and (cron.find("midterm.py") == -1 or cron.find("0 0 * * 0") == -1):
        # Schedule the script to run once per week at midnight on Sunday
        subprocess.run(
            f'(crontab -l ; echo "0 0 * * 0  /usr/bin/python3 {file_path} CRON >> {log_path} 2>&1") | crontab -',
            shell=True,
        )
    elif freq == "1":
        print("Already scheduled at this frequency")

    if freq == "2" and (cron.find("midterm.py") == -1 or cron.find("* * * * *") == -1):
        # Max cron frequency is every minute, so we need to create two entries
        # and offset them by 30 seconds to make it run more frequently
        subprocess.run(
            f'(crontab -l ; echo "* * * * * /usr/bin/python3 {file_path} CRON >> {log_path}") | crontab -',
            shell=True,
        )
        subprocess.run(
            f'(crontab -l ; echo "* * * * * (sleep 30 ; /usr/bin/python3 {file_path} CRON >> {log_path})") | crontab -',
            shell=True,
        )
    elif freq == "2":
        print("Already scheduled at this frequency")


def main(file_path: str):
    # List directories, files, and creation timestamp - move files to parent directory
    dirs = [file_path]
    dirs.extend(list_directories(file_path))
    print(dirs)
    for dir in dirs:
        # Get a list of files in the current directory
        files = list_files(dir)
        # If the list is not empty
        if files != []:
            # Move each file to its parent folder
            for file in files:
                print(f"File: {file} created on: {display_timestamp(file)}")
                move_file_up_one_level(file)

    # Remove any empty directories left after moving files
    remove_empty_directories(file_path)

    # Get a new listing of directories
    dirs = [file_path]
    dirs.extend(list_directories(file_path))
    for dir in dirs:
        # Get a list of files in the current directory
        files = list_files(dir)
        # If the list if not empty
        if files != []:
            # Sequentially rename each file and change its extension to csv
            for index, file in enumerate(files):
                rename_file(file, index + 1, "csv")

    # Get a new listing of directories
    dirs = [file_path]
    dirs.extend(list_directories(file_path))
    backdate_system_date()
    for dir in dirs:
        # Get a list of files in the current directory
        files = list_files(dir)
        # If the list if not empty
        if files != []:
            # Change the creation date for each file
            for file in files:
                change_creation_datetime(file)
    reset_system_date()

    # Generate a list of subdirectories
    dirs = [file_path]
    dirs.extend(list_directories(file_path))
    for dir in dirs:
        # Get a list of files in the current directory
        files = list_files(dir)
        # If the list is not empty
        if files != []:
            # Print the new altered timestamps
            for file in files:
                print(f"File: {file} created on: {display_timestamp(file)}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "CRON":
        print(f"Ran on {datetime.datetime.now()} via cron")
    else:
        schedule_program()
    main("data")
