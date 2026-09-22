import os
import re
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

    print("Final path: ", finalPath)
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
    finalTime = ""
    winner = 0

    params = {
        "count": 1
    }

    response = requests.get("https://api.mcsrranked.com/users/katchper/matches", params=params)

    if response.status_code == 200:

        match_result = response.json()
        timeVal = match_result["data"][0]["result"]["time"] / 1000
        winner_player = match_result["data"][0]["result"]["uuid"]
        forfeited = match_result["data"][0]["forfeited"]

        minute = int(timeVal // 60)
        second = int(timeVal % 60)
        finalTime = f"{minute}:{second}"


        settings = loadSettings()

        if winner_player != "None":
            if settings["uuid"] == winner_player:
                if forfeited:
                    winner = 2
                else:
                    winner = 1
            else:
                winner = 3


    return winner, finalTime

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
        print("settings file not found")

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



def rename_latest_recording(self):
    recordings_path = r"C:\Users\Katch\Videos"  # folder path

    files = [f for f in os.listdir(recordings_path) if f.endswith(".mp4")]
    latest_file = max(
        files,
        key=lambda f: os.path.getctime(os.path.join(recordings_path, f))
    )
    if self.ended:
        new_name = f"COMPLETE-mcsrranked_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.mp4"
    else:
        new_name = f"mcsrranked_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.mp4"
    latest_file = os.path.join(r"C:\Users\Katch\Videos", latest_file)
    new_name = os.path.join(r"C:\Users\Katch\Videos", new_name)
    self.rename_recording(latest_file, new_name)
    time.sleep(0.3)
    self.sort_recordings()


def sort_recordings(self):
    # OPEN RECORDINGS FOLDER -
    # READ WHAT FILES ARE THERE
    # IF video FILE NAME DOES NOT COMTAIN - COMPLETE - >  delete if older than x days long (default = 3)
    # check the file names
    # use regex or string eval to check for date in the video file name
    # for remaining videos, check if a folder for the date exists else, create a folder for the date
    # iterate over all videos moving them accordingly.

    print("Sorting recordings...")
    recordings_path = r"C:\Users\Katch\Videos"

    CompletedRuns = Path(recordings_path + "/CompletedRuns")
    NotCompletedRuns = Path(recordings_path + "/NotCompletedRuns")

    CompletedRuns.mkdir(exist_ok=True)
    NotCompletedRuns.mkdir(exist_ok=True)

    for f in os.listdir(recordings_path):
        if os.path.isfile(os.path.join(recordings_path, f)):
            if f.endswith(".mp4"):
                match = re.search(r"\d{4}-\d{2}-\d{2}", f)
                if match:
                    FileLocation = '/NotCompletedRuns'
                    matchDate = re.search(r"COMPLETE", f)
                    if matchDate:
                        FileLocation = '/CompletedRuns'

                    recording_date = match.group()
                    convertedDate = datetime.strptime(match.group(), "%Y-%m-%d").date()

                    if date.today() - timedelta(days=4) >= convertedDate and FileLocation == '/NotCompletedRuns':
                        fileToDelete = Path(recordings_path + "/" + f)
                        fileToDelete.unlink(missing_ok=True)
                    else:

                        folderstring = recordings_path + FileLocation + "/" + recording_date
                        folderpath = Path(folderstring)
                        folderpath.mkdir(exist_ok=True)

                        startString = recordings_path + "/" + f

                        startDirectory = Path(startString)
                        print(startString)
                        destinationString = folderstring + "/" + f
                        destinationDirectory = Path(destinationString)

                        print(destinationString)
                        shutil.move(startDirectory, destinationDirectory)