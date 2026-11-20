import json
import os
from pathlib import Path

import keyring
from platformdirs import user_config_dir
import datetime


APP_NAME = "MCSRRecordingTool"


def create_logfile(logging_enabled):
    if logging_enabled:
        # Create Log Folder
        config_dir = Path(user_config_dir(APP_NAME))
        config_dir = config_dir / 'logs'
        config_dir.mkdir(parents=True, exist_ok=True)

        x = datetime.datetime.now()
        write_to_logfile(logging_enabled, "App Started")


def write_to_logfile(logging_enabled, text):

    if logging_enabled:
        config_dir = Path(user_config_dir(APP_NAME))
        config_dir = config_dir / 'logs'

        x = datetime.datetime.now()
        log_name = f"{x.strftime('%Y_%m_%d')}.log"
        log_path = config_dir / log_name


        f = open(log_path, "a")
        f.write(x.strftime('%x %X') +" "+ text + "\n")
        f.close()



def delete_old_logs():
    log_path = Path(user_config_dir(APP_NAME))
    log_path = log_path / 'logs'

    for f in os.listdir(log_path):
        full_log_path = os.path.join(log_path, f)

        if os.path.isfile(full_log_path):
            if f.endswith(".log"):

                x = datetime.datetime.now() - datetime.timedelta(days=7)
                log_name = f"{x.strftime('%Y_%m_%d')}.log"

                if log_name > f:
                    os.remove(full_log_path)

