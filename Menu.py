import sys
import threading
from tkinter import filedialog

import customtkinter as ctk
from obsws_python import ReqClient

from General import *

APP_NAME = "MCSRRecordingTool"
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.title("MCSR Ranked Recording Tool")
        self.geometry("520x420")
        self.minsize(450, 350)
        self.ended = False
        self.settings = {}
        self.watcher_running = False
        self.obs_recording = False
        self.iconbitmap(self.resource_path("Icon.ico"))
        self.obs_recording = False
        self.resizable(False, False)

        threading.Thread(
            target=self.watch_log,
            daemon=True
        ).start()

        # container
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # pages
        self.pages = {}
        self.pages["menu"] = MainMenu(self.container, self)
        self.pages["settings"] = SettingsPage(self.container, self)


        for p in self.pages.values():
            p.grid(row=0, column=0, sticky="nsew")

        self.show_page("menu")

    def resource_path(self, filename):
        if getattr(sys, "frozen", False):
            return os.path.join(sys._MEIPASS, filename)
        return os.path.join(os.path.dirname(__file__), filename)

    def show_page(self, name):
        if name == "settings":
            self.minsize(500, 750)
            self.watcher_running = False
            self.stop_recording()
            #print(self.watcher_running)
            #print(self.watcher_running)
        else:
            self.minsize(450, 300)

        self.pages[name].tkraise()

    def on_close(self):
        # stop any running state safely
        self.watcher_running = False
        self.stop_recording()
        # optional: cleanup settings or save here
        #print("Closing app safely...")

        # destroy everything properly
        self.destroy()

    def watch_log(self):
        try:
            settings = loadSettings()
            log_path = os.path.join(settings["mc_path"], "latest.log")  # latest.log
            with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                # Ignore existing contents
                f.seek(0, 2)

                while True:
                    line = f.readline()

                    if not line:
                        time.sleep(0.05)
                        continue

                    # Watcher disabled?
                    if not self.watcher_running:
                        continue

                    line = line.strip()

                    record_status = readLogLine(line)
                    #print(record_status)
                    if record_status == 1:
                        self.start_recording()

                    elif record_status == 2:
                        self.stop_recording()
        except:
            pass


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
            #print("Recording started")

    def stop_recording(self):
        if self.obs_recording:
            self.obs.stop_record()
            self.obs_recording = False
            rename_latest_recording()
            #("Recording stopped")



'''
MAIN MENU SCREEN 

CONTAINS START/STOP BUTTON

ALSO CONTAINS SETTING BUTTON
'''


class MainMenu(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        ctk.CTkLabel(
            self,
            text="MCSR Ranked Recording Tool",
            font=ctk.CTkFont(size=26, weight="bold")
        ).pack(pady=(60, 30))

        # START BUTTON
        self.start_btn = ctk.CTkButton(
            self,
            fg_color="#c84d44",
            hover_color="#9c3d37",
            # #349136FF for green #276A28FF for green hover
            width=300,
            height=70,
            font=ctk.CTkFont(size=28, weight="bold"),
            text="Start",
            command=self.toggle_watcher

        )
        self.start_btn.pack(pady=20)

        # SETTINGS BUTTON

        ctk.CTkButton(
            self,
            fg_color="#136462",
            hover_color="#0b3a39",
            width=150,
            height=50,
            text="Settings",
            command=self.settingsNav,
        ).pack(pady=20)

    def settingsNav(self):
        if self.app.watcher_running:
            self.toggle_watcher()
            app.stop_recording()
        app.show_page("settings")

    def toggle_watcher(self):
        settings = loadSettings()
        self.app.watcher_running = not self.app.watcher_running

        if "Yes" in str(settings["obs_auto_open"]) and self.app.watcher_running:
            if not obs_is_running():
                subprocess.Popen(settings["obs_path"], shell=True)


        try:
            if "username" in settings:
                if self.app.watcher_running:
                    self.start_btn.configure(text="Stop", fg_color="#44a334",hover_color="#307224")
                else:
                    self.start_btn.configure(text="Start", fg_color="#c84d44",hover_color="#9c3d37")
        except:
            self.app.watcher_running = not self.app.watcher_running


"""
SETTINGS PAGE
"""

class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        # =========================
        # GENERAL SETTINGS
        # =========================

        general_frame = ctk.CTkFrame(self)
        general_frame.pack(
            fill="x",
            padx=20,
            pady=10
        )

        ctk.CTkLabel(
            general_frame,
            text="General Settings",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=10)

        general_table = ctk.CTkFrame(
            general_frame,
            fg_color="transparent"
        )
        general_table.pack(
            fill="x",
            padx=15,
            pady=(0, 15)
        )

        general_table.grid_columnconfigure(1, weight=1)
        general_table.grid_columnconfigure(2, weight=0)

        ctk.CTkLabel(
            general_table,
            text="Username:"
        ).grid(
            row=0,
            column=0,
            padx=10,
            pady=5,
            sticky="w"
        )


        self.username_entry = ctk.CTkEntry(
            general_table,
        )
        self.username_entry.grid(
            row=0,
            column=1,
            padx=10,
            pady=5,
            sticky="ew"
        )

        ctk.CTkLabel(
            general_table,
            text="Minecraft Log Directory:"
        ).grid(
            row=1,
            column=0,
            padx=10,
            pady=5,
            sticky="w"
        )

        self.mc_path_entry = ctk.CTkEntry(
            general_table
        )

        self.mc_path_entry.grid(
            row=1,
            column=1,
            padx=10,
            pady=5,
            sticky="ew"
        )

        ctk.CTkButton(
            general_table,
            width=70,
            fg_color="#c84d44",
            hover_color="#9c3d37",
            text="Select",
            command=self.pick_dir

        ).grid(
            row=1,
            column=2,
            padx=10,
            pady=5,
        )

        ctk.CTkLabel(
            general_table,
            text="Video Sorting"
        ).grid(
            row=2,
            column=0,
            padx=10,
            pady=5,
            sticky="w"
        )

        self.mode_dropdown = ctk.CTkOptionMenu(
            general_table,
            values=["No Sorting", "By Date and Completion Status"]
        )

        self.mode_dropdown.grid(
            row=2,
            column=1,
            padx=10,
            pady=5,
            sticky="w"
        )

        # =========================
        # RECORDING SETTINGS
        # =========================

        recording_frame = ctk.CTkFrame(self)
        recording_frame.pack(
            fill="x",
            padx=20,
            pady=10
        )

        ctk.CTkLabel(
            recording_frame,
            text="OBS Settings",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=10)

        recording_table = ctk.CTkFrame(
            recording_frame,
            fg_color="transparent"
        )
        recording_table.pack(
            fill="x",
            padx=15,
            pady=(0, 15)
        )

        recording_table.grid_columnconfigure(1, weight=1)
        recording_table.grid_columnconfigure(2, weight=0)

        ctk.CTkLabel(
            recording_table,
            text="Video Output Directory:"
        ).grid(
            row=0,
            column=0,
            padx=10,
            pady=5,
            sticky="w"
        )

        self.video_path_entry = ctk.CTkEntry(
            recording_table
        )

        self.video_path_entry.grid(
            row=0,
            column=1,
            padx=10,
            pady=5,
            sticky="ew"
        )
        ctk.CTkButton(
            recording_table,
            width=70,
            fg_color="#c84d44",
            hover_color="#9c3d37",
            text="Select",
            command=self.pick_recording_dir

        ).grid(
            row=0,
            column=2,
            padx=10,
            pady=5,
        )

        ctk.CTkLabel(
            recording_table,
            text="OBS Websocket Port:"
        ).grid(
            row=1,
            column=0,
            padx=10,
            pady=5,
            sticky="w"
        )

        self.websocket_port_entry = ctk.CTkEntry(
            recording_table,
        )
        self.websocket_port_entry.grid(
            row=1,
            column=1,
            padx=10,
            pady=5,
            sticky="ew"
        )
        ctk.CTkLabel(
            recording_table,
            text="OBS Websocket Server:"
        ).grid(
            row=2,
            column=0,
            padx=10,
            pady=5,
            sticky="w"
        )

        self.websocket_server_entry = ctk.CTkEntry(
            recording_table,
        )
        self.websocket_server_entry.grid(
            row=2,
            column=1,
            padx=10,
            pady=5,
            sticky="ew"
        )
        ctk.CTkLabel(
            recording_table,
            text="OBS Websocket Password"
        ).grid(
            row=3,
            column=0,
            padx=10,
            pady=5,
            sticky="w"
        )

        self.recording_pass_entry = ctk.CTkEntry(
            recording_table,
            show="*"
        )

        self.recording_pass_entry.grid(
            row=3,
            column=1,
            padx=10,
            pady=5,
            sticky="ew"
        )

        ctk.CTkLabel(
            recording_table,
            text="Auto Open OBS"
        ).grid(
            row=4,
            column=0,
            padx=10,
            pady=5,
            sticky="w"
        )

        self.obs_dropdown = ctk.CTkOptionMenu(
            recording_table,
            values=["Yes", "No"]
        )

        self.obs_dropdown.grid(
            row=4,
            column=1,
            padx=10,
            pady=5,
            sticky="w"
        )

        ctk.CTkLabel(
            recording_table,
            text="OBS link directory"
        ).grid(
            row=5,
            column=0,
            padx=10,
            pady=5,
            sticky="w"
        )

        self.obs_path_entry = ctk.CTkEntry(
            recording_table
        )

        self.obs_path_entry.grid(
            row=5,
            column=1,
            padx=10,
            pady=5,
            sticky="ew"
        )
        ctk.CTkButton(
            recording_table,
            width=70,
            fg_color="#c84d44",
            hover_color="#9c3d37",
            text="Select",
            command=self.pick_obs_dir

        ).grid(
            row=5,
            column=2,
            padx=10,
            pady=5,
        )


        # =========================
        # API KEY
        # =========================

        api_frame = ctk.CTkFrame(self)
        api_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            api_frame,
            text="API Key",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=10)

        api_table = ctk.CTkFrame(
            api_frame,
            fg_color="transparent"
        )

        api_table.pack(
            fill="x",
            padx=15,
            pady=(0, 15)
        )

        api_table.grid_columnconfigure(1, weight=1)
        api_table.grid_columnconfigure(2, weight=0)

        ctk.CTkLabel(
            api_table,
            text="**IGNORE** API Key:"
        ).grid(
            row=0,
            column=0,
            padx=10,
            pady=5,
            sticky="w"
        )

        self.api_key_entry = ctk.CTkEntry(
            api_table,
            show="*"
        )

        self.api_key_entry.grid(
            row=0,
            column=1,
            padx=10,
            pady=5,
            sticky="ew"
        )

        self.test_api_button = ctk.CTkButton(
            api_table,
            width=70,
            fg_color="#1d6866",
            hover_color="#174f4e",
            text="Test",
            command=self.testAPI
        )

        self.test_api_button.grid(
            row=0,
            column=2,
            padx=10,
            pady=5,
        )

        # =========================
        # IMPORT / EXPORT BUTTONS
        # =========================

        import_export_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        import_export_frame.pack(
            fill="x",
            padx=20,
            pady=(5, 5)
        )

        ctk.CTkButton(
            import_export_frame,
            text="Import",
            width=60,
            height=30,
            command = self.import_settings
        ).pack(
            side="right",
            padx=(0, 45)
        )

        ctk.CTkButton(
            import_export_frame,
            text="Export",
            width=60,
            height=30,
            command = self.export_settings
        ).pack(
            side="right",
            padx=10
        )

        # =========================
        # CANCEL / SAVE BUTTONS
        # =========================

        action_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        action_frame.pack(
            fill="x",
            padx=20,
            pady=(5, 20)
        )

        ctk.CTkButton(
            action_frame,
            text="Cancel",
            width=180,
            height=50,
            command=lambda: app.show_page("menu")
        ).pack(
            side="left",
            expand=True,
            padx=(0, 10)
        )

        ctk.CTkButton(
            action_frame,
            text="Save",
            width=180,
            height=50,
            command=self.save_settings
        ).pack(
            side="right",
            expand=True,
            padx=(10, 0)
        )
        self.load_settings()

    def load_settings(self):
        config_dir = Path(user_config_dir(APP_NAME))
        config_dir.mkdir(parents=True, exist_ok=True)
        settings_file = config_dir / "settings.json"
        try:
            with settings_file.open("r", encoding="utf-8") as f:
                settings = json.load(f)
        except:
            #print("no settings")
            pass
        try:
            self.username_entry.delete(0, "end")
            self.username_entry.insert(0, settings["username"])
        except:
            #print("error")
            pass

        try:
            self.mc_path_entry.delete(0, "end")
            self.mc_path_entry.insert(0, settings["mc_path"])
        except:
            #print("error")
            pass

        try:
            self.mode_dropdown.set(settings["video_sort"])
        except:
            #print("error")
            pass

        try:
            self.video_path_entry.delete(0, "end")
            self.video_path_entry.insert(0, settings["video_path"])
        except:
            #print("error")
            pass

        try:
            self.websocket_port_entry.delete(0, "end")
            self.websocket_port_entry.insert(0, settings["obs_port"])
        except:
            #print("error")
            pass

        try:
            self.websocket_server_entry.delete(0, "end")
            self.websocket_server_entry.insert(0, settings["obs_server"])
        except:
            #print("error")
            pass

        try:
            if keyring.get_password(APP_NAME, "OBSPASS") != "None":
                self.recording_pass_entry.delete(0, "end")
                self.recording_pass_entry.insert(0, keyring.get_password(APP_NAME, "OBSPASS"))
        except:
            #print("error")
            pass
        try:
            if keyring.get_password(APP_NAME, "API") != "None":
                self.api_key_entry.delete(0, "end")
                self.api_key_entry.insert(0, keyring.get_password(APP_NAME, "API"))
        except:
            #print("error")
            pass

        try:
            self.obs_path_entry.delete(0, "end")
            self.obs_path_entry.insert(0, settings["obs_path"])
        except:
            #print("error")
            pass

        try:
            self.obs_dropdown.set(settings["obs_auto_open"])
        except:
            #print("error")
            pass


    def save_settings(self):
        config_dir = Path(user_config_dir(APP_NAME))
        config_dir.mkdir(parents=True, exist_ok=True)
        settings_file = config_dir / "settings.json"

        #print("Saving settings...")

        settings = {
            "username": self.username_entry.get(),
            "uuid": getUUID(self.username_entry.get()),
            "mc_path": self.mc_path_entry.get(),
            "video_sort": self.mode_dropdown.get(),

            "video_path": self.video_path_entry.get(),
            "obs_port": self.websocket_port_entry.get(),
            "obs_server": self.websocket_server_entry.get(),
            "obs_auto_open": self.obs_dropdown.get(),
            "obs_path": self.obs_path_entry.get(),
        }

        with settings_file.open("w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)

        keyring.set_password(APP_NAME, "OBSPASS", self.recording_pass_entry.get())
        keyring.set_password(APP_NAME, "API", self.api_key_entry.get())

        # Save your settings here
        self.app.show_page("menu")


    def export_settings(self):
        config_dir = Path(user_config_dir(APP_NAME))
        config_dir.mkdir(parents=True, exist_ok=True)
        settings_file = config_dir / "settings.json"

        with settings_file.open("r", encoding="utf-8") as f:
            settings = json.load(f)

        settings["obs_pass"] = keyring.get_password(APP_NAME, "OBSPASS")
        settings["api_pass"] = keyring.get_password(APP_NAME, "API")

        file_path = filedialog.asksaveasfilename(
            title="Save Settings",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=4)

    def import_settings(self):
        file_path = filedialog.askopenfilename(
            title="Load Settings",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                settings = json.load(f)

        keyring.set_password(APP_NAME, "OBSPASS", settings["obs_pass"])
        keyring.set_password(APP_NAME, "API", settings["api_pass"])

        config_dir = Path(user_config_dir(APP_NAME))
        config_dir.mkdir(parents=True, exist_ok=True)
        settings_file = config_dir / "settings.json"

        del settings["obs_pass"]
        del settings["api_pass"]

        with settings_file.open("w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)

        self.load_settings()


    def pick_obs_dir(self):
        directory = os.path.join(
            os.getenv("PROGRAMDATA"),
            "Microsoft",
            "Windows",
            "Start Menu",
            "Programs"
        )

        path = filedialog.askopenfilename(
            parent=self.master,
            initialdir=directory,
            title="Load Settings",
            filetypes=[("Shortcut", "*.lnk"), ("All files", "*.*")]
        )

        if path:
            self.obs_path_entry.delete(0, "end")
            self.obs_path_entry.insert(0, path)


    def pick_dir(self):
        directory = findMCPath()
        path = filedialog.askdirectory(parent=self.master,initialdir=directory)
        if path:
            self.mc_path_entry.delete(0, "end")
            self.mc_path_entry.insert(0, path)



    def pick_recording_dir(self):
        directory = os.getenv("APPDATA")
        path = filedialog.askdirectory(parent=self.master,initialdir=directory)
        if path:
            self.video_path_entry.delete(0, "end")
            self.video_path_entry.insert(0, path)


    def testAPI(self):
        response = requests.get("https://api.mcsrranked.com/users/katchper/matches")
        #print(response.status_code)
        if response.status_code == 200:
            self.test_api_button.configure(
                fg_color="#2bb041",
                hover_color="#1a6c28",
                text="Pass",
            )
        else:
            self.test_api_button.configure(
                fg_color="#863120",
                hover_color="#68281c",
                text="Fail",
            )



if __name__ == "__main__":
    app = App()
    app.mainloop()