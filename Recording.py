from obsws_python import ReqClient
from General import *

def connectOBS(self):
    settings = loadSettings()

    self.obs = ReqClient(
        host=settings["obs_server"],
        port=settings["obs_port"],
        password=settings["obs_pass"]
    )

def start_recording(self):
    if not hasattr(self, "obs"):
        self.connectOBS()

    if not self.obs_recording:
        self.obs.start_record()
        self.obs_recording = True
        print("Recording started")


def stop_recording(self):
    if self.obs_recording:
        self.obs.stop_record()
        self.obs_recording = False
        print("Recording stopped")

        self.rename_latest_recording()
        self.ended = False