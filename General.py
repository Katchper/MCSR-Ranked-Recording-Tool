import os
import re
import subprocess

import keyring
import requests
import json
from platformdirs import user_config_dir
from datetime import date, timedelta
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


def findMCPath():
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


def getUUID(username):
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

def checkGameStatus():
    settings = loadSettings()

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


        settings = loadSettings()

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

def loadSettings():
    settings = ""
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

# reads a line of a log file
# 0 = skip
# 1 = start recording
# 2 = stop recording
def readLogLine(line):
    result = 0
    if (
            "[WorldCreator] Match initializing" in line
    ):
        result = 1


    # Stop recording
    elif (
            "[WorldCreator] Stopping" in line
            and "mcsrranked" in line
    ):
        result = 2

    return result

# win, time = checkGameStatus()



def rename_latest_recording():
    winner, finaltime, seed = checkGameStatus()
    #print(finaltime)
    settings = loadSettings()

    recordings_path = settings["video_path"]  # folder path

    files = [f for f in os.listdir(recordings_path) if f.endswith(".mp4")]
    latest_file = max(
        files,
        key=lambda f: os.path.getctime(os.path.join(recordings_path, f))
    )
    if winner == 1:
        new_name = f"Won_{seed}_{finaltime}.mp4"
    elif winner == 2:
        new_name = f"Won_FF_{seed}_{finaltime}.mp4"
    elif winner == 3:
        new_name = f"Lost_{seed}_{finaltime}.mp4"
    else:
        new_name = f"Incomplete_{seed}_{finaltime}.mp4"

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


def sort_recordings(recording_path):
    # OPEN RECORDINGS FOLDER -
    # READ WHAT FILES ARE THERE
    # IF video FILE NAME DOES NOT COMTAIN - COMPLETE - >  delete if older than x days long (default = 3)
    # check the file names
    # use regex or string eval to check for date in the video file name
    # for remaining videos, check if a folder for the date exists else, create a folder for the date
    # iterate over all videos moving them accordingly.

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
            if f.endswith(".mp4"):

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

#print(obs_is_running())