import os
import re
import subprocess

import keyring
import requests
import json
from platformdirs import user_config_dir
from pathlib import Path
from datetime import datetime
import time
import shutil

APP_NAME = "MCSRRecordingTool"

# Function to find the most suitable file path for the MCSR Logs Folder
# I start by going to APPDATA Path, looking for prism launcher filename
# if i find it then i try and find an instance containing MCSR in the name
#
# - Folder containing MCSR  > Returns that as the filePAth
# - Multipler folders containing MCSR > Returns Prism Launmcher instances path
# - No folders containing MCSR > Returns Prism Launmcher instances path
# - else return APPDATA FOLDER

VIDEO_EXTS = (".mp4", ".mov", ".avi", ".mkv", ".ts", ".flv")

def find_mc_path():
    appdata = os.getenv("APPDATA")
    #print(appdata)
    AppDataPath = appdata + r"\PrismLauncher\instances"
    #print(AppDataPath)
    AppDataPath = Path(AppDataPath)
    finalPath = AppDataPath

    counter = 0
    if AppDataPath.exists():
        #print("exists")
        subfolders = [p for p in AppDataPath.iterdir() if p.is_dir()]
        for folder in subfolders:
            if "MCSR" in folder.name.upper():
                #print(folder)
                finalPath = folder
                finalPath2 = finalPath / "minecraft"
                if finalPath2.exists():
                    finalPath = finalPath2
                counter = counter + 1
        if counter > 1:
            finalPath = AppDataPath
    else :
        finalPath = os.getenv("APPDATA")

    #print("Final path: ", finalPath)
    return finalPath



# Call to retrieve the UUID of the player, needed to identify the winner of a game


def get_uuid(username):
    uuid = ""
    response = requests.get(
        f"https://api.mojang.com/users/profiles/minecraft/{username}"
    )

    if response.status_code == 200:
        uuid = response.json()["id"]

    return uuid



## this method will check the last game, it will then return a number based on who won as well as the final time of the run
## winner variable results
# 0 = none
# 1 = you
# 2 = you by forfeit
# 3 = opponent

def check_game_status():
    settings = load_settings()

    finalTime = "111.111"
    winner = 0
    seed_type = "None"
    params = {
        "count": 1
    }

    response = requests.get("https://api.mcsrranked.com/users/"+settings["username"]+"/matches", params=params)

    if response.status_code == 200:

        match_result = response.json()
        timeVal = match_result["data"][0]["result"]["time"] / 1000
        winner_player = match_result["data"][0]["result"]["uuid"]
        forfeited = match_result["data"][0]["forfeited"]
        seed_type = match_result["data"][0]["seedType"]

        minute = int(timeVal // 60)
        second = int(timeVal % 60)
        if second < 10:
            second = "0" + str(second)
        finalTime = f"{minute}.{second}"


        settings = load_settings()

        if str(winner_player) != "None":
            if settings["uuid"] == str(winner_player):
                if forfeited:
                    winner = 2
                else:
                    winner = 1
            else:
                winner = 3


    return winner, finalTime, seed_type

# CURRENT SETTINGS SAVED
#  "username"
#  "uuid":
#  "mc_path"
#  "video_sort"
#  "video_path"
#  "obs_port"
#  "obs_server"
#  obs_pass
#  api_pass
#  "obs_auto_open"
#  "obs_path"
#  "ninjabrain_dropdown"
#  "ninjabrain_path_entry"

def load_settings():
    settings = {}
    config_dir = Path(user_config_dir(APP_NAME))
    config_dir.mkdir(parents=True, exist_ok=True)
    settings_file = config_dir / "settings.json"
    try:
        with settings_file.open("r", encoding="utf-8") as f:
            settings = json.load(f)

        settings["obs_pass"] = keyring.get_password(APP_NAME, "OBSPASS")
        settings["api_pass"] = keyring.get_password(APP_NAME, "API")

    except:
        #print("settings file not found")
        pass

    return settings


## test settings method, returns the missing ones
# required is passed through as a list of json variable names eg: ("username", "uuid"..)

def settings_validation(required):
    settings = load_settings()
    #print(settings)
    missing = required - settings.keys()
    return missing



# reads a line of a log file
# 0 = skip
# 1 = start recording
# 2 = stop recording
# 3 = seed change flag
def read_log_line(line):
    result = 0

    if (
            "[WorldCreator] creating new queue" in line
    ):
        result = 1


    # Stop recording
    elif (
            "[WorldCreator] Stopping" in line
            and "mcsrranked" in line
    ):
        result = 2

    elif (
            "Everyone has agreed to the seed change vote" in line
    ):
        result = 3

    return result


# Checks the seed_change_flag
# if 0 = the game result is checked to determine the winner
# if 1 = the recording is marked as a seed change
# if 2 = the recording is marked as disrupted.

def rename_latest_recording(seed_change_flag):
    global winner, seed, finaltime

    if seed_change_flag == 0:
        winner, finaltime, seed = check_game_status()
    elif seed_change_flag == 1:
        winner = 4
        finaltime = datetime.now().strftime("%H.%M.%S")
        seed = "SeedChanged"
    elif seed_change_flag == 2:
        winner = 4
        finaltime = datetime.now().strftime("%H.%M.%S")
        seed = "AppClosed"
    #print(finaltime)
    settings = load_settings()

    recordings_path = settings["video_path"]  # folder path

    files = [f for f in os.listdir(recordings_path) if f.endswith(VIDEO_EXTS)]
    latest_file = max(
        files,
        key=lambda f: os.path.getctime(os.path.join(recordings_path, f))
    )
    root, ext = os.path.splitext(latest_file)
    if winner == 1:
        new_name = f"Won_{seed}_{finaltime}{str(ext)}"
    elif winner == 2:
        new_name = f"Won_FF_{seed}_{finaltime}{str(ext)}"
    elif winner == 3:
        new_name = f"Lost_{seed}_{finaltime}{str(ext)}"
    else:
        new_name = f"Incomplete_{seed}_{finaltime}{str(ext)}"

    latest_file = os.path.join(recordings_path, latest_file)
    new_name = os.path.join(recordings_path, new_name)

    rename_recording(latest_file, new_name, settings["video_path"])

    time.sleep(0.3)
    if "By Date and Completion Status" in str(settings["video_sort"]):
        #print("test")
        sort_recordings(settings["video_path"])

def rename_recording(old_path, new_path, recording_path):
    if wait_for_file_release(old_path, recording_path):
        os.rename(old_path, new_path)
    else:
        pass
        #print("File still locked — rename skipped")



def wait_for_file_release(path1, recording_path, timeout=10):
    start = time.time()
    timeout = float(timeout)
    while time.time() - start < timeout:
        try:
            targetpath = os.path.join(recording_path, path1)
            os.rename(targetpath, targetpath)
            return True
        except PermissionError:
            time.sleep(0.2)
    return False

# OPEN RECORDINGS FOLDER -
    # READ WHAT FILES ARE THERE
    # XXXX (Not current) - IF video FILE NAME DOES NOT COMTAIN - COMPLETE - >  delete if older than x days long (default = 3)
    # check the file names
    # use regex or string eval to check for date in the video file name
    # for remaining videos, check if a folder for the date exists else, create a folder for the date
    # iterate over all videos moving them accordingly.

def sort_recordings(recording_path):

    #print("Sorting recordings...")
    recordings_path = recording_path

    #print(recordings_path)

    WonRuns = Path(recordings_path + "/WonRuns")
    LostRuns = Path(recordings_path + "/LostRuns")
    OtherRuns = Path(recordings_path + "/OtherRuns")

    WonRuns.mkdir(exist_ok=True)
    LostRuns.mkdir(exist_ok=True)
    OtherRuns.mkdir(exist_ok=True)


    for f in os.listdir(recordings_path):
        video_path = os.path.join(recordings_path, f)
        #print(video_path)
        #print(f)
        if os.path.isfile(video_path):
            #print("ISFILE")
            if f.endswith(VIDEO_EXTS):

                match = re.search(r"\d+.\d+", f)
                #print(match)

                if match:
                    #print("confirm")
                    FileLocation = '/OtherRuns'
                    matchDate = re.search(r"Won", f)
                    if matchDate:
                        FileLocation = '/WonRuns'

                    matchDate = re.search(r"Lost", f)
                    if matchDate:
                        FileLocation = '/LostRuns'
                    #print(FileLocation)


                    convertedDate = datetime.fromtimestamp(os.path.getmtime(video_path)).date()

                    ## NEEDS REWORKING
                    """
                    if date.today() - timedelta(days=4) >= convertedDate and FileLocation == '/LostRuns':
                        fileToDelete = Path(recordings_path + "/" + f)
                        fileToDelete.unlink(missing_ok=True)

                    elif date.today() - timedelta(days=4) >= convertedDate and FileLocation == '/OtherRuns':
                        fileToDelete = Path(recordings_path + "/" + f)
                        fileToDelete.unlink(missing_ok=True)
                    """

                    folderstring = recordings_path + FileLocation + "/" + str(convertedDate)
                    folderpath = Path(folderstring)
                    folderpath.mkdir(exist_ok=True)

                    startString = recordings_path + "/" + f

                    startDirectory = Path(startString)
                    #print(startString)
                    destinationString = folderstring + "/" + f
                    destinationDirectory = Path(destinationString)

                    #print(destinationString)
                    shutil.move(startDirectory, destinationDirectory)

#rename_latest_recording()
#sort_recordings(r"C:/Users/Katch/Videos")


def obs_is_running():
    result = subprocess.run(
        ["tasklist", "/FI", "IMAGENAME eq obs64.exe"],
        capture_output=True,
        text=True
    )
    return "obs64.exe" in result.stdout


def ninja_is_running():
    settings = load_settings()
    ninjabrain_name = os.path.basename(settings["ninja_path"])
    result = subprocess.run(
        [
            "powershell",
            "-Command",
            "Get-CimInstance Win32_Process -Filter \"Name = 'javaw.exe'\" | "
            "Select-Object -ExpandProperty CommandLine"
        ],
        capture_output=True,
        text=True
    )

    return str(ninjabrain_name) in result.stdout

#print(ninja_is_running())


#print(obs_is_running())