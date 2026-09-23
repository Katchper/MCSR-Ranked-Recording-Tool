# MCSR Ranked Recording Tool Version 1.0

A tool for automatically starting and stopping recordings for MCSR Ranked games.

The tool removes the need to manually manage recordings and makes it easier to organise and manage your gameplay footage.

## Features

- 🎥 Automatically starts OBS recording when an MCSR Ranked game begins
- ⏹️ Automatically stops OBS recording when the game ends
- 📁 Automatically organises recorded videos
- 🏷️ Automatically generates video titles
- 💾 Saves your settings between sessions and versions
- 🔧 Supports OBS Studio

## Requirements

- Windows
- OBS Studio
- Minecraft
- MCSR Ranked

## Quick Start Guide

### 1. Download the Executable

Download the latest `.exe` from the **Releases** page.

### 2. Open the App

Launch `MCSR Ranked Recording Tool.exe`.

### 3. Configure Settings

Open the **Settings** page and configure General and OBS settings:

- Minecraft Username
- Minecraft Log Directory
    (Will attempt to auto locate example being: `C:\Users\YourUser\AppData\Roaming\PrismLauncher\instances\MCSRRanked\minecraft\logs`)
- Video Sorting
- Video Output Directory
    (default in OBS being `C:/Users/YourUser/Videos`)
- OBS Websocket settings (port, server, password which can be found in obs under tools > websocket server settings)
- Auto Open OBS (When start button is pressed, it will check if already open)
- OBS link directory
    (needs to be mapped to a .lnk program opens start menu by default example being `C:/ProgramData/Microsoft/Windows/Start Menu/Programs/OBS Studio.lnk`)
  
- API Key **CAN BE IGNORED*
### 4. Save Your Settings

Click **Save** to save your configuration. I would highly recommend restarting the recording tool after this step currently.

### 5. Start Recording

Press **Start**.

The tool will monitor your MCSR Ranked game and automatically manage the recording.

## Video Organisation

Recordings can be automatically organised into folders based on the game information.

For example:

```text
Recordings/
├──Completed Runs/
│    ├── 2026-09-22/
│    │   └──  11-38 - Desert Temple.mp4
│    │   └── ...
